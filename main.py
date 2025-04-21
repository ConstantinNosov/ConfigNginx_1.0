from ssh_client import SSHClient
from text_file_modifier import TextFileModifier
import os

def main():
    while True: 
        file_extension = ".conf" 
        file_path = "conf.d/"  
        hostname = "ahmad.ftc.ru"  
        port = 22                       
        username = "nginx"      
        key_file = r"C:\STORAGE\Key\key" 
        bname = input("Введи имя конфига, или '0' для выхода:")
        if bname.lower() == '0':  
            break       
        remote_file_path =  f'{file_path}{bname}{file_extension}'  
        local_file_path = f'{bname}{file_extension}' 
        
        # Загрузка файла с сервера
        while True:
            ssh_client = SSHClient(hostname, port, username, key_file)
            ssh_client.connect()   
            result_download = ssh_client.download_file_with_replacement(remote_file_path, local_file_path)           
            if result_download:
                ssh_client.close()
                break  
            else:
                bname = input("Файл не найден. Введи имя конфига, или '0' для выхода:")
                if bname.lower() == '0':
                    return  
                remote_file_path = f'{file_path}{bname}{file_extension}'  
                local_file_path = f'{bname}{file_extension}' 
                ssh_client.close()
                
        # Новое значение cert
        while True:    
            try:
                new_cert = int(input("Введи новый cert 1, 3 или 0 для перезапуска: "))
                if new_cert == 0:
                    main()
                    return 
                if new_cert in [1, 3]:
                    old_cert = 3 if new_cert == 1 else 1
                    break  
                else:
                    print("Некорректный ввод. Введи 1, 3 или 0 для перезапуска.")
            except ValueError:
                print("Некорректный ввод. Введи 1, 3 или 0 для перезапуска.")
                
        print(f"Новое значение cert: {new_cert}")
        in_new_sert = f"proxy_pass https://sbpgs-cert{new_cert}.cbrpay.ru:9443;"
        in_old_sert = f"proxy_pass https://sbpgs-cert{old_cert}.cbrpay.ru:9443;"
        print(in_new_sert)
    
        # Выполняем замену по тексу конфига
        modifier = TextFileModifier(local_file_path)
        result_modifier = modifier.replace_text(in_old_sert, in_new_sert)
        if not result_modifier:
            if os.path.exists(local_file_path):
                os.remove(local_file_path)              
            print("Замена не была произведена текущие значения cert совпадают с введенным.")
            continue 
           
        # Выгружаем файл на сервер, с заменой существующего файла
        ssh_client = SSHClient(hostname, port, username, key_file)
        ssh_client.connect()
        result_upload = ssh_client.upload_file_with_replacement(local_file_path, remote_file_path)
        if not result_upload:
            print(f'Ошибка выгрузки файла на {hostname}')
            ssh_client.close()
            continue      
        ssh_client.close()
        
        # Удаляем локальный файл
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
                       
        # Перезапуск, проверка статуса Nginx
        ssh_client = SSHClient(hostname, port, username, key_file)
        try:
            ssh_client.connect()               
            restart = 'sudo systemctl restart nginx'
            stdout, stderr = ssh_client.execute_command(restart)
            if stderr:
                print("Ошибка перезагрузки Nginx")
                print(stderr)
            else:
                print("Конфиг обновлен")

            status = 'systemctl status nginx'
            stdout, stderr = ssh_client.execute_command(status)
            if stdout:
                print(stdout)
                if "active (running)" in stdout:
                    print("Конфин обновлен.")
                    print("Nginx успешно перезагружен.")
                    print("Cтатус: active (running)")
            else:
                print("Nginx не запущен!")
            if stderr:
                print("Ошибка проверки статуса:")
                print(stderr)
        finally:
            ssh_client.client.close()
        
if __name__ == "__main__":
    main()