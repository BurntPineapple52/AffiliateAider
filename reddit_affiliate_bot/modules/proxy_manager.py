import random
import time
from typing import List, Optional, Dict
from dataclasses import dataclass
from loguru import logger
from config import ProxyConfig

@dataclass
class ProxyStats:
    proxy_id: str
    last_used: float
    success_count: int
    error_count: int
    response_time: float

class ProxyManager:
    """Manages rotation and monitoring of proxy connections"""
    
    def __init__(self, proxies: List[ProxyConfig]):
        self.proxies = proxies
        self.proxy_stats = []
        
        for proxy in proxies:
            self.proxy_stats.append(ProxyStats(
                proxy_id=f"{proxy.protocol}://{proxy.host}:{proxy.port}",
                last_used=0,
                success_count=0,
                error_count=0,
                response_time=0
            ))
        logger.info(f"Initialized proxy manager with {len(proxies)} proxies")

    def get_proxy_dict(self, proxy: ProxyConfig) -> Optional[Dict]:
        """Convert ProxyConfig to requests-compatible proxy dict"""
        if not proxy.enabled:
            return None
            
        proxy_url = f"{proxy.protocol}://"
        if proxy.username and proxy.password:
            proxy_url += f"{proxy.username}:{proxy.password}@"
        proxy_url += f"{proxy.host}:{proxy.port}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }

    def get_next_proxy(self, strategy: str = "round_robin") -> Optional[ProxyConfig]:
        """Get next available proxy based on rotation strategy"""
        if not self.proxies:
            return None

        if strategy == "random":
            return random.choice(self.proxies)

        # Default round-robin strategy
        current_idx = min(
            range(len(self.proxy_stats)),
            key=lambda i: self.proxy_stats[i].last_used
        )
        
        self.proxy_stats[current_idx].last_used = time.time()
        return self.proxies[current_idx]

    def update_stats(self, proxy_id: str, success: bool, response_time: float):
        """Update proxy usage statistics"""
        for stats in self.proxy_stats:
            if stats.proxy_id == proxy_id:
                if success:
                    stats.success_count += 1
                else:
                    stats.error_count += 1
                stats.response_time = response_time
                break

    def get_best_proxy(self) -> Optional[ProxyConfig]:
        """Get the proxy with highest success rate and fastest response time"""
        if not self.proxy_stats:
            return None
            
        # Calculate score for each proxy (higher is better)
        scored_proxies = []
        for stats in self.proxy_stats:
            total = stats.success_count + stats.error_count
            success_rate = stats.success_count / total if total > 0 else 0
            score = success_rate * 0.7 + (1 / (stats.response_time + 0.1)) * 0.3
            scored_proxies.append((score, stats.proxy_id))
            
        # Sort by score descending
        scored_proxies.sort(reverse=True, key=lambda x: x[0])
        best_id = scored_proxies[0][1]
        return self.get_by_id(best_id)

    def get_by_id(self, proxy_id: str) -> Optional[ProxyConfig]:
        """Get proxy config by its identifier"""
        for i, stats in enumerate(self.proxy_stats):
            if stats.proxy_id == proxy_id:
                return self.proxies[i]
        return None

    def disable_proxy(self, proxy_id: str):
        """Disable a problematic proxy"""
        proxy = self.get_by_id(proxy_id)
        if proxy:
            proxy.enabled = False
            logger.warning(f"Disabled proxy {proxy_id} due to failures")
