import asyncio
import aiohttp
import json

async def check_token_permissions():
    """Check token permissions and info"""
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    access_token = config['instagram']['access_token']
    api_version = config['instagram']['api_version']
    
    print("=" * 80)
    print("CHECKING ACCESS TOKEN PERMISSIONS")
    print("=" * 80)
    print(f"Access Token: {access_token[:30]}...{access_token[-20:]}")
    print()
    
    async with aiohttp.ClientSession() as session:
        # Debug token to see permissions
        print("Fetching token information...")
        url = f'https://graph.facebook.com/{api_version}/debug_token'
        params = {
            'input_token': access_token,
            'access_token': access_token
        }
        
        async with session.get(url, params=params) as resp:
            print(f"Status Code: {resp.status}")
            result = await resp.json()
            
            if resp.status == 200 and 'data' in result:
                data = result['data']
                print("\n✅ Token Information:")
                print(f"  App ID: {data.get('app_id', 'N/A')}")
                print(f"  Type: {data.get('type', 'N/A')}")
                print(f"  Valid: {data.get('is_valid', False)}")
                print(f"  Expires: {data.get('expires_at', 'Never')}")
                print(f"  User ID: {data.get('user_id', 'N/A')}")
                
                if 'scopes' in data:
                    print(f"\n  Permissions (Scopes):")
                    for scope in data['scopes']:
                        print(f"    • {scope}")
                else:
                    print("\n  ⚠️ No scopes/permissions found")
            else:
                print(f"\n❌ Failed to debug token:")
                print(json.dumps(result, indent=2))
        
        print("\n" + "-" * 80)
        
        # Try to get basic user info
        print("\nFetching user information...")
        url = f'https://graph.facebook.com/{api_version}/me'
        params = {
            'fields': 'id,name',
            'access_token': access_token
        }
        
        async with session.get(url, params=params) as resp:
            result = await resp.json()
            if resp.status == 200:
                print(f"✅ User: {result.get('name')} (ID: {result.get('id')})")
            else:
                print(f"❌ Error: {result.get('error', {}).get('message', 'Unknown error')}")
    
    print("\n" + "=" * 80)
    print("\nREQUIRED PERMISSIONS for Instagram Messaging:")
    print("  • pages_read_engagement")
    print("  • pages_messaging")
    print("  • instagram_basic")
    print("  • instagram_manage_messages")
    print("\nMake sure to generate token from Graph API Explorer with these permissions.")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(check_token_permissions())
