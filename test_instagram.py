import asyncio
import aiohttp
import json

async def test_instagram_api():
    """Test Instagram Graph API credentials"""
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    access_token = config['instagram']['access_token']
    page_id = config['instagram']['page_id']
    api_version = config['instagram']['api_version']
    
    print("=" * 60)
    print("Testing Instagram Graph API")
    print("=" * 60)
    print(f"Page ID: {page_id}")
    print(f"API Version: {api_version}")
    print(f"Access Token: {access_token[:20]}...{access_token[-20:]}")
    print()
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Get page info
        print("Test 1: Fetching page information...")
        url = f'https://graph.facebook.com/{api_version}/{page_id}'
        params = {
            'fields': 'id,name,followers_count,instagram_business_account',
            'access_token': access_token
        }
        
        async with session.get(url, params=params) as resp:
            print(f"Status Code: {resp.status}")
            result = await resp.json()
            
            if resp.status == 200:
                print("✅ SUCCESS - Page info retrieved:")
                print(f"   Page ID: {result.get('id')}")
                print(f"   Page Name: {result.get('name', 'N/A')}")
                print(f"   Followers: {result.get('followers_count', 'N/A')}")
                if 'instagram_business_account' in result:
                    print(f"   Instagram Business Account: {result['instagram_business_account']['id']}")
                    ig_account_id = result['instagram_business_account']['id']
                else:
                    print("   No Instagram Business Account linked")
                    ig_account_id = None
            else:
                print(f"❌ FAILED - Error:")
                print(json.dumps(result, indent=2))
                return
        
        print()
        
        # Test 2: Get Instagram account info (if available)
        if ig_account_id:
            print("Test 2: Fetching Instagram Business Account info...")
            url = f'https://graph.facebook.com/{api_version}/{ig_account_id}'
            params = {
                'fields': 'id,username,name,profile_picture_url,followers_count',
                'access_token': access_token
            }
            
            async with session.get(url, params=params) as resp:
                print(f"Status Code: {resp.status}")
                result = await resp.json()
                
                if resp.status == 200:
                    print("✅ SUCCESS - Instagram account info:")
                    print(f"   Username: @{result.get('username', 'N/A')}")
                    print(f"   Name: {result.get('name', 'N/A')}")
                    print(f"   Followers: {result.get('followers_count', 'N/A')}")
                else:
                    print(f"❌ FAILED - Error:")
                    print(json.dumps(result, indent=2))
    
    print()
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_instagram_api())
