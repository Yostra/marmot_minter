import asyncio
from pathlib import Path
import aiofiles
import aiohttp
from requests.utils import unquote_unreserved


async def create_nft_image(custom_text: str) -> str:
    """
    create dalle image and return saved image path
    """
    bearer = "Bearer sess-xxxx"
    headers = {"Authorization": bearer}

    image_headers = {'accept-encoding': 'gzip, deflate, br',
               "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"}

    caption = custom_text

    # Modify the caption

    print(f"Caption: {caption}")

    url = "https://labs.openai.com/api/labs/tasks"
    request_json = {
        "task_type": "text2im",
        "prompt": {
            "caption": caption,
            "batch_size": 4
        }
    }

    task_base = "https://labs.openai.com/api/labs/tasks/"
    async with aiohttp.ClientSession(headers=headers) as session:
        response = await session.post(url, json=request_json)
        json_response = await response.json()
        task_id = json_response["id"]
        task_url = f"{task_base}{task_id}"

        while True:
            task_response = None
            task_counter = 0
            task_json = None
            while True:
                task_response = await session.get(task_url)
                try:
                    task_json = await task_response.json()
                    break
                except:
                    await asyncio.sleep(3)
                    task_counter += 1
                    print(f"Error x1")
                    if task_counter == 5:
                        return
                    pass

            status = task_json["status"]
            if status == "pending":
                print("waiting")
                await asyncio.sleep(10)
                continue

            if status != "succeeded":
                print(f"Status {status}")

                if status == "cancelled" or status == "failed":
                    print(f"error: {status}")
                    print(f"error: {task_json}")
                    response = await session.post(url, json=request_json)
                    json_response = await response.json()
                    task_id = json_response["id"]
                    task_url = f"{task_base}{task_id}"
                    await asyncio.sleep(3)
                    continue

                if status == "rejected":
                    print(f"error: {status}")
                    print(f"error: {task_json}")
                    if "attacks" in request_json["prompt"]["caption"]:
                        request_json["prompt"]["caption"] = request_json["prompt"]["caption"].replace("attacks", "")

                    response = await session.post(url, json=request_json)
                    json_response = await response.json()
                    task_id = json_response["id"]
                    task_url = f"{task_base}{task_id}"
                    await asyncio.sleep(3)
                    continue
                await asyncio.sleep(3)
                print(f"error: {status}")
                print(task_json)
                continue
            image_path = None

            for i in range(0, 4):
                image_url = task_json["generations"]["data"][i]["generation"]["image_path"]

                image_path = Path(
                    f"image_tasks/{task_id}_{i}.png"
                )
                image_url = unquote_unreserved(image_url)

                async with aiohttp.ClientSession(headers=image_headers) as image_session:
                    async with image_session.get(image_url) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(image_path.absolute(), mode="wb")
                            await f.write(await resp.read())
                            await f.close()

            return f"{image_path.absolute()}"

        return ""
