class TextFileModifier:
    def __init__(self, file_path):
        self.file_path = file_path

   #Замена строк
    def replace_text(self, old_text, new_text):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        original_content = content  # Сохраняем оригинальное содержимое для сравнения  
        new_content = content.replace(old_text, new_text)
        with open(self.file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
            
            # Проверка успешности замены
        if original_content != new_content:
            return True
        else:
            return False
