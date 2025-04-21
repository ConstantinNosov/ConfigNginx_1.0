import paramiko
import os

class SSHClient:
    def __init__(self, hostname, port, username, key_file):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.key_file = key_file
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            self.client.connect(self.hostname, port=self.port, username=self.username, key_filename=self.key_file)
            print(f"Успешно подключено к {self.hostname}:{self.port} как {self.username}")
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            
    # Выполняет команду на сервере 
    def execute_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode(), stderr.read().decode()
             
    # Загрузка файла с сервера с заменой       
    def download_file_with_replacement(self, remote_file_path, local_file_path):
        sftp_client = self.client.open_sftp()
        try:
            # Проверяем, существует ли удаленный файл
            sftp_client.stat(remote_file_path)  # Если файл не найден, будет вызвано исключение
            sftp_client.get(remote_file_path, local_file_path)
            return True  
        except FileNotFoundError:
            print(f"Файл {remote_file_path} не найден. Уточните имя и повторите ввод.")
            return False 
        except paramiko.SSHException as ssh_error:
            print(f"Ошибка SSH: {ssh_error}")
            return False
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return False 
        finally:
            sftp_client.close()
                  
    # Загрузка файла на сервер с заменой      
    def upload_file_with_replacement(self, local_file_path, remote_file_path):
        sftp_client = None
        try:       
            if not os.path.exists(local_file_path):   # Проверка существования локального файла
                print(f"Локальный файл {local_file_path} не найден.")
                return False           
            sftp_client = self.client.open_sftp()
            sftp_client.put(local_file_path, remote_file_path)
            print(f"Файл {local_file_path} успешно обновлен на ahmad.ftc.ru {remote_file_path}")
            return True 
        except paramiko.SSHException as ssh_error:
            print(f"Ошибка SSH: {ssh_error}")
            return False
        except FileNotFoundError as fnf_error:
            print(f"Ошибка: {fnf_error}")
            return False
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return False
        finally:
            if sftp_client:
                sftp_client.close()
                
    def close(self):
        self.client.close()