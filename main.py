from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import aiohttp
from bs4 import BeautifulSoup

app = FastAPI()


async def fetch_html(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                raise HTTPException(
                    status_code=response.status, detail="Failed to fetch HTML"
                )


async def extract_favicon_from_html(html: str, base_url: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    icon_link = (
        soup.find("link", rel="icon")
        or soup.find("link", rel="shortcut icon")
        or soup.find("link", rel="apple-touch-icon")
    )

    if icon_link and icon_link.get("href"):
        href = icon_link["href"]
        if href.startswith("http"):
            return href
        else:
            return f"{base_url.rstrip('/')}/{href.lstrip('/')}"
    else:
        raise HTTPException(status_code=404, detail="Favicon not found in HTML")


async def fetch_favicon(url: str) -> str:
    # 尝试从根目录获取 favicon.ico
    favicon_url = f"{url.rstrip('/')}/favicon.ico"
    async with aiohttp.ClientSession() as session:
        async with session.get(favicon_url) as response:
            if response.status == 200:
                return favicon_url

    # 尝试从 HTML 页面中提取 favicon 链接
    html = await fetch_html(url)
    return await extract_favicon_from_html(html, url)


@app.get("/favicon")
async def get_favicon(website: str):
    try:
        favicon_url = await fetch_favicon(website)
        return RedirectResponse(url=favicon_url)
    except HTTPException as e:
        raise e


# 启动服务
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80a00)
