import base64
import re
import json
from openai import OpenAI
from elasticsearch import Elasticsearch

# Initialize OpenAI client
client = OpenAI(
    api_key="key"
)

# Initialize Elasticsearch client
es = Elasticsearch("http://host.docker.internal:9200")  # Adjust if needed


# Function to extract JSON from GPT response
def extract_json(text):
    # Remove ```json or ``` wrappers
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


# Function to push to Elasticsearch
def push_to_elasticsearch(username, data):
    index_name = f"{username}_data".lower()

    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)

    es.index(index=index_name, document=data)


def flatten_order_data(data):
    flattened_data = []
    order_id = data.get("Order ID")
    address = data.get("Address delivered")
    date = data.get("Date")
    time = data.get("Time")
    total_amount = data.get("Total Amount")

    for item in data.get("Purchased Items", []):
        # Flatten each item and add order level details
        flattened_item = {
            "Order ID": order_id,
            "Address delivered": address,
            "Date": date,
            "Time": time,
            "Total Amount": total_amount,
            "name": item.get("name"),
            "quantity": item.get("quantity"),
            "price": item.get("price"),
            "category": item.get("category")
        }
        flattened_data.append(flattened_item)

    return flattened_data


def process_order_images(username, image_paths):
    image_contents = []
    for image_path in image_paths:
        with open(image_path, "rb") as image_file:
            b64_image = base64.b64encode(image_file.read()).decode("utf-8")
            image_contents.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{b64_image}"}
            })

    prompt = """
            You are an assistant that extracts grocery order details from screenshots of receipts.
            Categories - ['Fruits & Vegetables', 'Beverages', 'Dairy', 'Snacks', 'Personal Grooming', 'Sexual Wellness', 
            'Electronics', 'Clothes & Accessories', 'Others']
            Extract:
            - Order ID
            - Address delivered
            - Date in yyyy-mm-dd format
            - Time in hh:mm:ss (24hours) format
            - Total Amount
            - A list of purchased items (from all receipts), with quantity, price, and categorize them into categories given above.

            Respond in formatted json. No currency in amount fields. Just numeric value.
            """

    messages = [
        {
            "role": "user",
            "content": [{"type": "text", "text": prompt}] + image_contents
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
        max_tokens=2000  # increase if needed
    )

    text_output = response.choices[0].message.content.strip()
    data = extract_json(text_output)

    data = flatten_order_data(data)

    resp = json.dumps(data, indent=2)
    print(resp)

    # Push to Elasticsearch
    print("Pushing to ES")
    for data_point in data:
        push_to_elasticsearch(username, data_point)
