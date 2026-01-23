"""Quick API test script - 快速测试脚本"""

import asyncio
import httpx
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


async def test_health_check():
    """测试健康检查接口"""
    print("\n" + "=" * 60)
    print("1. 测试健康检查接口")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False


async def test_generate_api():
    """测试生成接口"""
    print("\n" + "=" * 60)
    print("2. 测试生成接口")
    print("=" * 60)
    
    request_data = {
        "title": "如何制作美味拿铁",
        "steps": [
            {
                "title": "研磨咖啡豆",
                "description": "选择新鲜的中深烘焙豆子"
            },
            {
                "title": "萃取浓缩",
                "description": "使用咖啡机萃取双份Espresso"
            },
            {
                "title": "打奶泡",
                "description": "将牛奶加热并打出细腻奶泡"
            },
            {
                "title": "组合完成",
                "description": "将奶泡倒入浓缩咖啡中"
            }
        ],
        "visual_preferences": {
            "character": "bear",
            "color_scheme": "pastel",
            "custom_tags": ["kawaii", "flat"]
        }
    }
    
    print(f"\n发送请求:")
    print(json.dumps(request_data, indent=2, ensure_ascii=False))
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            # 创建任务
            response = await client.post(
                f"{BASE_URL}/api/v1/generate",
                json=request_data
            )
            print(f"\n状态码: {response.status_code}")
            result = response.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if response.status_code != 200:
                return None
            
            task_id = result.get("task_id")
            print(f"\n✅ 任务创建成功，task_id: {task_id}")
            
            return task_id
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            return None


async def test_get_status(task_id: str):
    """测试状态查询接口"""
    print("\n" + "=" * 60)
    print("3. 测试状态查询接口")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 轮询查询状态
            max_attempts = 30
            for i in range(max_attempts):
                print(f"\n第 {i+1} 次查询...")
                response = await client.get(f"{BASE_URL}/api/v1/generate/{task_id}")
                
                if response.status_code != 200:
                    print(f"❌ 状态码: {response.status_code}")
                    return False
                
                result = response.json()
                status = result.get("status")
                progress = result.get("progress", 0)
                message = result.get("message", "")
                
                print(f"状态: {status} | 进度: {progress}% | {message}")
                
                if status == "completed":
                    print("\n✅ 任务完成！")
                    print("\n完整响应:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))
                    return True
                
                elif status == "failed":
                    print("\n❌ 任务失败")
                    error = result.get("error", {})
                    print(f"错误: {error}")
                    return False
                
                # 等待一段时间再查询
                await asyncio.sleep(2)
            
            print("\n⚠️ 超时：任务未在预期时间内完成")
            return False
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False


async def main():
    """主测试流程"""
    print("\n" + "=" * 60)
    print("🚀 Nano Flow API 测试")
    print("=" * 60)
    print(f"API 地址: {BASE_URL}")
    print("\n请确保:")
    print("1. 后端服务已启动 (python run.py)")
    print("2. .env 文件已正确配置 API 密钥")
    
    # 等待用户确认
    input("\n按 Enter 键开始测试...")
    
    # 1. 健康检查
    health_ok = await test_health_check()
    if not health_ok:
        print("\n❌ 健康检查失败，请检查服务是否正常启动")
        return
    
    print("\n✅ 健康检查通过")
    
    # 2. 创建生成任务
    task_id = await test_generate_api()
    if not task_id:
        print("\n❌ 创建任务失败")
        return
    
    # 3. 查询任务状态
    success = await test_get_status(task_id)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️ 测试未完全通过，请查看上面的错误信息")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
