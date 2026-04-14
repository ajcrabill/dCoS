"""
Backend Executor - Abstraction layer for different LLM backends.

Supports:
- Claude via Cowork
- Local LLMs via Ollama
- OpenCoWork
- MLX (local)

Usage:
    executor = get_executor("ollama")
    response = executor.generate("Summarize this: " + text)
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Callable
import subprocess
import urllib.request
import urllib.error


class ExecutorBackend(ABC):
    """Abstract base class for LLM execution backends."""

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate a response to a prompt."""
        pass

    @abstractmethod
    def streaming_generate(self, prompt: str, callback: Optional[Callable] = None) -> str:
        """Generate with streaming support."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available/configured."""
        pass

    @abstractmethod
    def health_check(self) -> dict:
        """Return health status."""
        pass


class OllamaBackend(ExecutorBackend):
    """Local LLM execution via Ollama."""

    def __init__(self, config: dict):
        self.endpoint = config.get("endpoint", "http://localhost:11434")
        self.model = config.get("model", "mistral")
        self.timeout = config.get("timeout", 300)

    def is_available(self) -> bool:
        try:
            urllib.request.urlopen(f"{self.endpoint}/api/tags", timeout=5)
            return True
        except (urllib.error.URLError, urllib.error.HTTPError):
            return False

    def health_check(self) -> dict:
        if not self.is_available():
            return {"status": "unavailable", "message": "Ollama not responding"}

        try:
            url = f"{self.endpoint}/api/tags"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read().decode())
            models = [m["name"] for m in data.get("models", [])]

            return {
                "status": "healthy",
                "endpoint": self.endpoint,
                "current_model": self.model,
                "available_models": models,
                "model_available": self.model in models
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate using Ollama."""
        url = f"{self.endpoint}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature,
            "num_predict": max_tokens
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')
        except Exception as e:
            return f"Error: {str(e)}"

    def streaming_generate(self, prompt: str, callback: Optional[Callable] = None) -> str:
        """Generate with streaming support."""
        url = f"{self.endpoint}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "temperature": 0.7
        }

        full_response = ""
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                for line in response:
                    chunk = json.loads(line.decode('utf-8'))
                    token = chunk.get('response', '')
                    full_response += token
                    if callback:
                        callback(token)
            return full_response
        except Exception as e:
            return f"Error: {str(e)}"


class ClaudeCoworkBackend(ExecutorBackend):
    """Claude via Cowork execution."""

    def __init__(self, config: dict):
        self.config = config

    def is_available(self) -> bool:
        # Check if Cowork is available
        try:
            # This would check for Cowork socket/availability
            return True
        except:
            return False

    def health_check(self) -> dict:
        return {
            "status": "configured",
            "backend": "claude-cowork",
            "note": "Uses Cowork CLI interface"
        }

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate using Claude via Cowork."""
        # This would call through Cowork
        # For now, return placeholder
        return "Claude via Cowork - implementation requires Cowork integration"

    def streaming_generate(self, prompt: str, callback: Optional[Callable] = None) -> str:
        """Generate with streaming via Cowork."""
        return self.generate(prompt)


class OpenCoWorkBackend(ExecutorBackend):
    """OpenCoWork execution backend."""

    def __init__(self, config: dict):
        self.endpoint = config.get("endpoint", "http://localhost:5000")

    def is_available(self) -> bool:
        try:
            urllib.request.urlopen(f"{self.endpoint}/health", timeout=5)
            return True
        except:
            return False

    def health_check(self) -> dict:
        if not self.is_available():
            return {"status": "unavailable"}

        try:
            response = urllib.request.urlopen(f"{self.endpoint}/health", timeout=5)
            return json.loads(response.read().decode())
        except:
            return {"status": "error"}

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate using OpenCoWork."""
        url = f"{self.endpoint}/generate"
        data = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                result = json.loads(response.read().decode())
                return result.get('response', '')
        except Exception as e:
            return f"Error: {str(e)}"

    def streaming_generate(self, prompt: str, callback: Optional[Callable] = None) -> str:
        """Generate with streaming."""
        return self.generate(prompt)


class MLXBackend(ExecutorBackend):
    """MLX (Apple Silicon) local execution."""

    def __init__(self, config: dict):
        self.model = config.get("model", "mistral-7b")
        self.mlx_path = config.get("mlx_path", Path.home() / ".mlx-lm")

    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["mlx_lm.generate", "--help"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def health_check(self) -> dict:
        if not self.is_available():
            return {"status": "unavailable", "message": "MLX not installed"}

        return {
            "status": "available",
            "backend": "mlx",
            "model": self.model,
            "mlx_path": str(self.mlx_path)
        }

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate using MLX."""
        try:
            result = subprocess.run(
                [
                    "mlx_lm.generate",
                    "--model", self.model,
                    "--prompt", prompt,
                    "--max-tokens", str(max_tokens),
                    "--temperature", str(temperature)
                ],
                capture_output=True,
                timeout=300,
                text=True
            )
            return result.stdout
        except Exception as e:
            return f"Error: {str(e)}"

    def streaming_generate(self, prompt: str, callback: Optional[Callable] = None) -> str:
        """Generate with streaming (not fully supported)."""
        return self.generate(prompt)


def list_available_backends() -> dict:
    """Detect and list available backends."""
    backends = {}

    # Check Ollama
    try:
        test = OllamaBackend({"endpoint": "http://localhost:11434"})
        if test.is_available():
            backends["ollama"] = test.health_check()
    except:
        pass

    # Check MLX
    try:
        test = MLXBackend({})
        if test.is_available():
            backends["mlx"] = test.health_check()
    except:
        pass

    # Claude/Cowork is always an option if installed
    backends["claude-cowork"] = {"status": "optional", "note": "Requires Cowork installation"}
    backends["opencowork"] = {"status": "optional", "note": "Requires OpenCoWork installation"}

    return backends


def get_executor(backend_name: str, config_path: Optional[Path] = None) -> ExecutorBackend:
    """
    Get an executor backend by name.

    Args:
        backend_name: One of "ollama", "mlx", "claude-cowork", "opencowork"
        config_path: Path to backend config file

    Returns:
        ExecutorBackend instance
    """
    config = {}

    if config_path and config_path.exists():
        with open(config_path) as f:
            config = json.load(f)

    if backend_name == "ollama":
        return OllamaBackend(config)
    elif backend_name == "mlx":
        return MLXBackend(config)
    elif backend_name == "claude-cowork":
        return ClaudeCoworkBackend(config)
    elif backend_name == "opencowork":
        return OpenCoWorkBackend(config)
    else:
        raise ValueError(f"Unknown backend: {backend_name}. Available: ollama, mlx, claude-cowork, opencowork")
