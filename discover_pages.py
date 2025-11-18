import asyncio
import aiohttp
import json

async def discover_pages():
    """Discover all accessible pages with current access token"""
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    access_token = config['instagram']['access_token']
    api_version = config['instagram']['api_version']
    
    print("=" * 80)
    print("DISCOVERING ACCESSIBLE PAGES")
    print("=" * 80)
    print(f"API Version: {api_version}")
    print(f"Access Token: {access_token[:30]}...{access_token[-20:]}")
    print()
    
    async with aiohttp.ClientSession() as session:
        # Get user's pages
        print("Fetching accessible pages...")
        url = f'https://graph.facebook.com/{api_version}/me/accounts'
        params = {
            'access_token': access_token
        }
        
        async with session.get(url, params=params) as resp:
            print(f"Status Code: {resp.status}")
            result = await resp.json()
            
            if resp.status == 200:
                pages = result.get('data', [])
                
                if not pages:
                    print("❌ No pages found. This token may not have access to any pages.")
                    print("\nPlease ensure:")
                    print("1. The token has 'pages_read_engagement' permission")
                    print("2. You've granted access to your Facebook Page")
                    return
                
                print(f"\n✅ Found {len(pages)} page(s):\n")
                
                for i, page in enumerate(pages, 1):
                    print(f"Page {i}:")
                    print(f"  ID: {page.get('id')}")
                    print(f"  Name: {page.get('name')}")
                    print(f"  Access Token: {page.get('access_token', 'N/A')[:30]}...")
                    print()
                    
                    # Check if page has Instagram account
                    page_id = page.get('id')
                    page_token = page.get('access_token', access_token)
                    
                    ig_url = f'https://graph.facebook.com/{api_version}/{page_id}'
                    ig_params = {
                        'fields': 'instagram_business_account',
                        'access_token': page_token
                    }
                    
                    async with session.get(ig_url, params=ig_params) as ig_resp:
                        if ig_resp.status == 200:
                            ig_result = await ig_resp.json()
                            if 'instagram_business_account' in ig_result:
                                ig_id = ig_result['instagram_business_account']['id']
                                print(f"  ✅ Instagram Business Account: {ig_id}")
                                
                                # Get Instagram account details
                                ig_detail_url = f'https://graph.facebook.com/{api_version}/{ig_id}'
                                ig_detail_params = {
                                    'fields': 'username,name,followers_count',
                                    'access_token': page_token
                                }
                                
                                async with session.get(ig_detail_url, params=ig_detail_params) as detail_resp:
                                    if detail_resp.status == 200:
                                        detail = await detail_resp.json()
                                        print(f"     Username: @{detail.get('username', 'N/A')}")
                                        print(f"     Name: {detail.get('name', 'N/A')}")
                                        print(f"     Followers: {detail.get('followers_count', 'N/A')}")
                                        print(f"\n  📝 USE THIS PAGE ID IN CONFIG.JSON: {page_id}")
                            else:
                                print(f"  ⚠️  No Instagram Business Account linked")
                        print()
                        print("-" * 80)
            else:
                print(f"❌ FAILED - Error:")
                print(json.dumps(result, indent=2))
                print("\nThis usually means:")
                print("1. The token doesn't have 'pages_read_engagement' permission")
                print("2. The token is for a user account, not an app")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(discover_pages())
