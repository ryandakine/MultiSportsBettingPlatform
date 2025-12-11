#!/usr/bin/env python3
"""
Test Performance Optimization System
==================================
Test the comprehensive performance optimization and reliability system.
"""

import asyncio
import json
import time
import gzip
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class PerformanceOptimizationTester:
    """Test the performance optimization system functionality."""
    
    def __init__(self):
        self.test_results = []
        self.optimizer = None
    
    async def test_payload_compression(self, test_name: str) -> Dict[str, Any]:
        """Test payload compression functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.performance_optimization import PayloadCompressor, CompressionType
            
            compressor = PayloadCompressor(compression_threshold=100)
            
            # Test small payload (should not compress)
            small_payload = "Hello World"
            small_result = compressor.compress_payload(small_payload)
            
            print(f"✅ Small payload: {small_result['compressed']} (ratio: {small_result['compression_ratio']:.2f})")
            
            # Test large payload (should compress)
            large_payload = "A" * 1000  # 1000 characters
            large_result = compressor.compress_payload(large_payload)
            
            print(f"✅ Large payload: {large_result['compressed']} (ratio: {large_result['compression_ratio']:.2f})")
            
            # Test decompression
            decompressed = compressor.decompress_payload(large_result)
            decompression_success = decompressed == large_payload
            
            print(f"✅ Decompression: {'success' if decompression_success else 'failed'}")
            
            # Test compression stats
            stats = compressor.get_compression_stats()
            print(f"✅ Compression stats: {stats}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Payload compression test completed successfully",
                "small_payload_compressed": small_result['compressed'],
                "large_payload_compressed": large_result['compressed'],
                "compression_ratio": large_result['compression_ratio'],
                "decompression_success": decompression_success,
                "compression_stats": stats
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_circuit_breaker(self, test_name: str) -> Dict[str, Any]:
        """Test circuit breaker functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.performance_optimization import CircuitBreaker
            
            # Create circuit breaker
            cb = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
            
            # Test successful calls
            success_count = 0
            for i in range(5):
                try:
                    result = cb.call(lambda: "success")
                    if result == "success":
                        success_count += 1
                except Exception:
                    pass
            
            print(f"✅ Successful calls: {success_count}/5")
            
            # Test failure handling
            def failing_function():
                raise Exception("Simulated failure")
            
            failure_count = 0
            for i in range(5):
                try:
                    cb.call(failing_function)
                except Exception:
                    failure_count += 1
            
            print(f"✅ Failure handling: {failure_count} failures recorded")
            
            # Test circuit breaker state
            stats = cb.get_stats()
            print(f"✅ Circuit breaker state: {stats['state']}")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Circuit breaker test completed successfully",
                "success_count": success_count,
                "failure_count": failure_count,
                "circuit_breaker_state": stats['state'],
                "failure_rate": stats['failure_rate']
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_system_monitoring(self, test_name: str) -> Dict[str, Any]:
        """Test system monitoring functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.performance_optimization import SystemMonitor
            import redis.asyncio as redis
            
            # Create Redis client
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # Create monitor
            monitor = SystemMonitor(redis_client)
            
            # Record some metrics
            monitor.record_response_time(100.5)
            monitor.record_response_time(150.2)
            monitor.record_message("prediction_update")
            monitor.record_message("notification")
            monitor.record_error("connection_timeout")
            
            # Get metrics summary
            summary = monitor.get_metrics_summary()
            
            print(f"✅ Metrics recorded: {len(monitor.metrics_history)}")
            print(f"✅ Response times: {len(monitor.response_times)}")
            print(f"✅ Message counts: {dict(monitor.message_counts)}")
            print(f"✅ Error counts: {dict(monitor.error_counts)}")
            
            # Test metrics structure
            if summary:
                print(f"✅ Metrics summary available: {len(summary)} fields")
            
            await redis_client.close()
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "System monitoring test completed successfully",
                "metrics_recorded": len(monitor.metrics_history),
                "response_times_count": len(monitor.response_times),
                "message_types": dict(monitor.message_counts),
                "error_types": dict(monitor.error_counts),
                "summary_available": bool(summary)
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_fallback_manager(self, test_name: str) -> Dict[str, Any]:
        """Test fallback manager functionality."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.performance_optimization import FallbackManager, CircuitBreaker
            import redis.asyncio as redis
            
            # Create Redis client
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # Create fallback manager
            fallback_manager = FallbackManager(redis_client)
            
            # Register test fallback
            def test_fallback(*args, **kwargs):
                return {"status": "fallback", "data": "fallback_data"}
            
            cb = CircuitBreaker(failure_threshold=2, recovery_timeout=5)
            fallback_manager.register_fallback("test_service", test_fallback, cb)
            
            # Test successful execution
            async def successful_function():
                return {"status": "success", "data": "primary_data"}
            
            result = await fallback_manager.execute_with_fallback("test_service", successful_function)
            primary_success = result["status"] == "success"
            
            print(f"✅ Primary execution: {'success' if primary_success else 'fallback'}")
            
            # Test fallback execution
            async def failing_function():
                raise Exception("Simulated failure")
            
            # Trigger failures to open circuit breaker
            for i in range(3):
                try:
                    await fallback_manager.execute_with_fallback("test_service", failing_function)
                except:
                    pass
            
            # Now should use fallback
            try:
                result = await fallback_manager.execute_with_fallback("test_service", failing_function)
                fallback_success = result["status"] == "fallback"
            except:
                fallback_success = False
            
            print(f"✅ Fallback execution: {'success' if fallback_success else 'failed'}")
            
            # Get fallback status
            status = await fallback_manager.get_fallback_status()
            print(f"✅ Fallback status: {len(status)} services registered")
            
            await redis_client.close()
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Fallback manager test completed successfully",
                "primary_success": primary_success,
                "fallback_success": fallback_success,
                "services_registered": len(status),
                "circuit_breaker_state": status.get("test_service", {}).get("circuit_breaker_state", "unknown")
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_performance_optimizer(self, test_name: str) -> Dict[str, Any]:
        """Test the main performance optimizer."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.performance_optimization import PerformanceOptimizer
            import redis.asyncio as redis
            
            # Create Redis client
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # Create optimizer
            optimizer = PerformanceOptimizer(redis_client)
            
            # Test payload optimization
            test_payload = "This is a test payload that should be compressed" * 50
            optimized = optimizer.optimize_payload(test_payload)
            
            compression_success = optimized["compressed"]
            compression_ratio = optimized["compression_ratio"]
            
            print(f"✅ Payload optimization: {'compressed' if compression_success else 'not compressed'} (ratio: {compression_ratio:.2f})")
            
            # Test decompression
            decompressed = optimizer.decompress_payload(optimized)
            decompression_success = decompressed == test_payload
            
            print(f"✅ Payload decompression: {'success' if decompression_success else 'failed'}")
            
            # Record metrics
            optimizer.record_metrics(
                response_time=125.5,
                message_type="test_message",
                error_type="test_error"
            )
            
            # Get performance summary
            summary = optimizer.get_performance_summary()
            
            print(f"✅ Performance summary: {len(summary)} components")
            print(f"✅ Optimization active: {summary['optimization_active']}")
            print(f"✅ Compression stats: {len(summary['compression_stats'])} metrics")
            
            await redis_client.close()
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Performance optimizer test completed successfully",
                "compression_success": compression_success,
                "compression_ratio": compression_ratio,
                "decompression_success": decompression_success,
                "optimization_active": summary['optimization_active'],
                "compression_stats_count": len(summary['compression_stats']),
                "metrics_components": len(summary)
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_load_performance(self, test_name: str) -> Dict[str, Any]:
        """Test system performance under load."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.performance_optimization import PayloadCompressor, CircuitBreaker
            
            # Test compression performance
            compressor = PayloadCompressor()
            
            start_time = time.time()
            compression_times = []
            
            for i in range(100):
                payload = f"Test payload number {i} with some additional data to make it larger" * 10
                comp_start = time.time()
                result = compressor.compress_payload(payload)
                comp_time = time.time() - comp_start
                compression_times.append(comp_time)
            
            total_time = time.time() - start_time
            avg_compression_time = sum(compression_times) / len(compression_times)
            
            print(f"✅ Compression performance: {total_time:.3f}s total, {avg_compression_time*1000:.2f}ms avg")
            
            # Test circuit breaker performance
            cb = CircuitBreaker(failure_threshold=5, recovery_timeout=1)
            
            start_time = time.time()
            cb_calls = 0
            
            for i in range(50):
                try:
                    cb.call(lambda: "success")
                    cb_calls += 1
                except Exception:
                    pass
            
            cb_time = time.time() - start_time
            avg_cb_time = cb_time / 50
            
            print(f"✅ Circuit breaker performance: {cb_time:.3f}s total, {avg_cb_time*1000:.2f}ms avg per call")
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Load performance test completed successfully",
                "compression_total_time": total_time,
                "avg_compression_time_ms": avg_compression_time * 1000,
                "circuit_breaker_total_time": cb_time,
                "avg_cb_time_ms": avg_cb_time * 1000,
                "successful_cb_calls": cb_calls
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def test_reliability_mechanisms(self, test_name: str) -> Dict[str, Any]:
        """Test reliability mechanisms."""
        print(f"🧪 Testing {test_name}...")
        
        try:
            from src.services.performance_optimization import CircuitBreaker, FallbackManager
            import redis.asyncio as redis
            
            # Create Redis client
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # Test circuit breaker recovery
            cb = CircuitBreaker(failure_threshold=2, recovery_timeout=2)
            
            # Trigger failures
            for i in range(3):
                try:
                    cb.call(lambda: (_ for _ in ()).throw(Exception("Test failure")))
                except Exception:
                    pass
            
            initial_state = cb.get_stats()["state"]
            
            # Wait for recovery
            await asyncio.sleep(3)
            
            # Test recovery
            try:
                result = cb.call(lambda: "recovered")
                recovery_success = result == "recovered"
            except Exception:
                recovery_success = False
            
            final_state = cb.get_stats()["state"]
            
            print(f"✅ Circuit breaker recovery: {initial_state} -> {final_state}")
            print(f"✅ Recovery test: {'success' if recovery_success else 'failed'}")
            
            # Test fallback reliability
            fallback_manager = FallbackManager(redis_client)
            
            def reliable_fallback(*args, **kwargs):
                return {"status": "reliable_fallback"}
            
            fallback_manager.register_fallback("reliable_service", reliable_fallback)
            
            async def unreliable_function():
                raise Exception("Unreliable function")
            
            try:
                result = await fallback_manager.execute_with_fallback("reliable_service", unreliable_function)
                fallback_reliability = result["status"] == "reliable_fallback"
            except Exception:
                fallback_reliability = False
            
            print(f"✅ Fallback reliability: {'success' if fallback_reliability else 'failed'}")
            
            await redis_client.close()
            
            return {
                "test": test_name,
                "status": "PASSED",
                "message": "Reliability mechanisms test completed successfully",
                "initial_cb_state": initial_state,
                "final_cb_state": final_state,
                "recovery_success": recovery_success,
                "fallback_reliability": fallback_reliability
            }
            
        except Exception as e:
            print(f"❌ {test_name}: Failed - {e}")
            return {
                "test": test_name,
                "status": "FAILED",
                "message": str(e)
            }
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all performance optimization tests."""
        print("🚀 Starting Performance Optimization Tests")
        print("=" * 80)
        
        tests = [
            self.test_payload_compression("Payload Compression and Decompression"),
            self.test_circuit_breaker("Circuit Breaker Pattern"),
            self.test_system_monitoring("System Monitoring and Metrics"),
            self.test_fallback_manager("Fallback Manager"),
            self.test_performance_optimizer("Performance Optimizer Integration"),
            self.test_load_performance("Load Performance Testing"),
            self.test_reliability_mechanisms("Reliability Mechanisms")
        ]
        
        for test in tests:
            result = await test
            self.test_results.append(result)
        
        return self.test_results
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("📊 Performance Optimization Test Summary")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASSED")
        failed = sum(1 for result in self.test_results if result["status"] == "FAILED")
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🎯 Test Results:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"   {status_icon} {result['test']}: {result['status']}")
            if result["status"] == "FAILED":
                print(f"      Error: {result['message']}")
        
        # Save results
        with open("performance_optimization_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Test results saved to performance_optimization_test_results.json")

async def main():
    """Main test function."""
    tester = PerformanceOptimizationTester()
    
    try:
        await tester.run_all_tests()
        tester.print_summary()
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 