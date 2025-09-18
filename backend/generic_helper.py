import re


def extract_session_id(session_str: str):
    match = re.search(r"\/sessions\/(.*)\/contexts\/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string

    return ""


def get_str_from_food_dict(food_dict: dict):
    return ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])


if __name__ == "__main__":
    # print(extract_session_id("projects/panda-chatbot-9oad/agent/sessions/9ec56e61-48a6-6c4f-19bc-acf529b5fc14/contexts/ongoing-order"))
    print(get_str_from_food_dict({"chicken burger":2, "Coca-Cola":2, "Ice cream":1}))