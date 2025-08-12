import docker
import json
import logging
import os
from typing import Dict, List, Any
from app.config import settings

logger = logging.getLogger(__name__)


class SecurityToolRunner:
    """Runner for security tools in Docker containers"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.tools_config = self._load_tools_config()
    
    def _load_tools_config(self) -> Dict[str, Any]:
        """Load tools configuration from tools directory"""
        config_file = os.path.join(settings.tools_directory, "tools_config.json")
        
        if not os.path.exists(config_file):
            # Default configuration
            return {
                "metasploit": {
                    "image": "rapid7/metasploit-framework:latest",
                    "command": ["msfconsole", "-q", "-x"],
                    "environment": {},
                    "volumes": {},
                    "timeout": 1800  # 30 minutes
                },
                "openvas": {
                    "image": "immauss/openvas:latest",
                    "command": ["gvm-start"],
                    "environment": {},
                    "volumes": {},
                    "timeout": 3600  # 1 hour
                },
                "caldera": {
                    "image": "mitre/caldera:latest",
                    "command": ["python", "server.py"],
                    "environment": {},
                    "volumes": {},
                    "timeout": 1800  # 30 minutes
                }
            }
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading tools config: {e}")
            return {}
    
    def run_tool(self, tool_name: str, target_description: str, 
                 severity_level: str, attack_vectors: int) -> Dict[str, Any]:
        """Run a security tool with the given parameters"""
        
        if tool_name not in self.tools_config:
            raise ValueError(f"Tool {tool_name} not configured")
        
        config = self.tools_config[tool_name]
        
        try:
            # Prepare tool-specific parameters
            tool_params = self._prepare_tool_params(
                tool_name, target_description, severity_level, attack_vectors
            )
            
            # Run the tool in Docker
            result = self._run_docker_container(
                image=config["image"],
                command=config["command"],
                environment=config.get("environment", {}),
                volumes=config.get("volumes", {}),
                timeout=config.get("timeout", 1800),
                tool_params=tool_params
            )
            
            # Parse tool output
            parsed_result = self._parse_tool_output(tool_name, result)
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"Error running tool {tool_name}: {e}")
            return {
                "output": f"Error: {str(e)}",
                "vulnerabilities": [],
                "risk_score": 0
            }
    
    def _prepare_tool_params(self, tool_name: str, target_description: str,
                            severity_level: str, attack_vectors: int) -> Dict[str, Any]:
        """Prepare tool-specific parameters"""
        
        if tool_name == "metasploit":
            return {
                "target": target_description,
                "severity": severity_level,
                "vectors": attack_vectors,
                "script": f"""
                use auxiliary/scanner/portscan/tcp
                set RHOSTS {target_description}
                set THREADS {attack_vectors}
                run
                """
            }
        
        elif tool_name == "openvas":
            return {
                "target": target_description,
                "scan_config": f"Full and fast; {severity_level} priority",
                "max_hosts": attack_vectors
            }
        
        elif tool_name == "caldera":
            return {
                "target": target_description,
                "adversary": f"adversary_{severity_level}",
                "planner": "batch",
                "obfuscators": ["base64", "base64jumble"]
            }
        
        return {}
    
    def _run_docker_container(self, image: str, command: List[str], 
                            environment: Dict[str, str], volumes: Dict[str, Dict],
                            timeout: int, tool_params: Dict[str, Any]) -> str:
        """Run a Docker container with the specified configuration"""
        
        try:
            # Pull the image if it doesn't exist
            try:
                self.client.images.get(image)
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling image {image}")
                self.client.images.pull(image)
            
            # Prepare container configuration
            container_config = {
                "image": image,
                "command": command,
                "environment": environment,
                "volumes": volumes,
                "detach": False,
                "remove": True,
                "timeout": timeout
            }
            
            # Run the container
            logger.info(f"Running container with image {image}")
            container = self.client.containers.run(**container_config)
            
            # Get logs
            logs = container.decode('utf-8') if hasattr(container, 'decode') else str(container)
            
            return logs
            
        except docker.errors.ContainerError as e:
            logger.error(f"Container error: {e}")
            return f"Container error: {str(e)}"
        except docker.errors.ImageNotFound as e:
            logger.error(f"Image not found: {e}")
            return f"Image not found: {str(e)}"
        except Exception as e:
            logger.error(f"Docker error: {e}")
            return f"Docker error: {str(e)}"
    
    def _parse_tool_output(self, tool_name: str, output: str) -> Dict[str, Any]:
        """Parse tool-specific output and extract vulnerabilities"""
        
        vulnerabilities = []
        risk_score = 0
        
        if tool_name == "metasploit":
            # Parse Metasploit output
            if "open ports" in output.lower():
                vulnerabilities.append({
                    "type": "open_ports",
                    "description": "Open ports detected",
                    "severity": "medium"
                })
                risk_score += 30
            
            if "vulnerability" in output.lower():
                vulnerabilities.append({
                    "type": "vulnerability",
                    "description": "Security vulnerability detected",
                    "severity": "high"
                })
                risk_score += 70
        
        elif tool_name == "openvas":
            # Parse OpenVAS output
            if "high" in output.lower():
                vulnerabilities.append({
                    "type": "high_severity",
                    "description": "High severity vulnerability found",
                    "severity": "high"
                })
                risk_score += 80
            
            if "medium" in output.lower():
                vulnerabilities.append({
                    "type": "medium_severity",
                    "description": "Medium severity vulnerability found",
                    "severity": "medium"
                })
                risk_score += 50
        
        elif tool_name == "caldera":
            # Parse Caldera output
            if "success" in output.lower():
                vulnerabilities.append({
                    "type": "attack_success",
                    "description": "Attack simulation successful",
                    "severity": "high"
                })
                risk_score += 60
        
        # Ensure risk score is within bounds
        risk_score = min(100, max(0, risk_score))
        
        return {
            "output": output,
            "vulnerabilities": vulnerabilities,
            "risk_score": risk_score
        }
    
    def list_available_tools(self) -> List[str]:
        """List all available security tools"""
        return list(self.tools_config.keys())
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a specific tool"""
        if tool_name in self.tools_config:
            return self.tools_config[tool_name]
        return {} 