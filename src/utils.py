import os
import json
import logging

def load_messages_for_bot(file_name: str) -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, 'resources', f'{file_name}.txt')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def get_image_url(image_name: str) -> str:
    base_path = os.path.dirname(os.path.realpath(__file__))
    images = {
        "brain": os.path.join(base_path, 'resources', 'images', 'random.jpg'),
        "chat_gpt": os.path.join(base_path, 'resources', 'images', 'gpt.jpg'),
        "talk": os.path.join(base_path, 'resources', 'images', 'talk.png'),
        "quiz": os.path.join(base_path, 'resources', 'images', 'quiz.jpg'),
        "translator": os.path.join(base_path, 'resources', 'images', 'translator.png'),
        "resume": os.path.join(base_path, 'resources', 'images', 'resume.png')
    }
    return images.get(image_name, os.path.join(base_path, 'resources', 'images', 'placeholder.png'))