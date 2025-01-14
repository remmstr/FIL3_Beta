import os
import subprocess

def check_file_exists(filepath):
    """
    Vérifie si un fichier existe à un chemin spécifié.

    Args:
        filepath (str): Le chemin vers le fichier à vérifier.

    Raises:
        FileNotFoundError: Si le fichier n'est pas trouvé au chemin spécifié.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Le fichier spécifié est introuvable: {filepath}")
    
def check_adb_connection(platform_tools_path):
    """
    Vérifie la connexion ADB et démarre le serveur ADB si nécessaire.

    Args:
        platform_tools_path (str): Le chemin vers le dossier des outils de plateforme ADB.

    Returns:
        bool: True si la connexion ADB est réussie, False en cas d'échec.
    """
    try:
        os.environ["PATH"] += os.pathsep + platform_tools_path
        subprocess.check_output(["adb", "start-server"], stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur ADB : {e}")
        return False
    return True

def is_permission_granted(adb_exe_path, numero, package_name, permission):
    """
    Vérifie si une permission spécifique est accordée à une application.

    Args:
        adb_exe_path (str): Le chemin vers l'exécutable ADB.
        numero (str): Le numéro de série de l'appareil.
        package_name (str): Le nom du package de l'application.
        permission (str): La permission à vérifier.

    Returns:
        bool: True si la permission est accordée, False sinon.
    """
    try:
        check_command = [
            adb_exe_path, "-s", numero, "shell", "dumpsys", "package", package_name
        ]
        output = subprocess.check_output(check_command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8")
        return f"grantedPermissions: {permission}" in output
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la vérification de la permission {permission} : {e}")
        return False

def grant_permissions(adb_exe_path, numero, package_name):
    """
    Accorde les permissions nécessaires à une application.

    Args:
        adb_exe_path (str): Le chemin vers l'exécutable ADB.
        numero (str): Le numéro de série de l'appareil.
        package_name (str): Le nom du package de l'application.
    """
    permissions = [
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",
    ]
    for permission in permissions:
        if not is_permission_granted(adb_exe_path, numero, package_name, permission):
            full_command = [adb_exe_path, "-s", numero, "shell", "pm", "grant", package_name, permission]
            try:
                subprocess.run(full_command, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            except subprocess.CalledProcessError as e:
                pass

def is_device_awake(adb_exe_path, numero):
    """
    Vérifie si l'appareil est éveillé.

    Args:
        adb_exe_path (str): Le chemin vers l'exécutable ADB.
        numero (str): Le numéro de série de l'appareil.

    Returns:
        bool: True si l'appareil est éveillé, False sinon.
    """
    try:
        command = [adb_exe_path, "-s", numero, "shell", "dumpsys power | grep 'Display Power'"]
        output = subprocess.check_output(command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8')
        if 'state=ON' in output:
            return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la vérification de l'état de l'appareil : {e}")
    return False

def wake_up_device(adb_exe_path, numero):
    """
    Réveille l'appareil s'il est en veille.

    Args:
        adb_exe_path (str): Le chemin vers l'exécutable ADB.
        numero (str): Le numéro de série de l'appareil.
    """
    if not is_device_awake(adb_exe_path, numero):
        command = [adb_exe_path, "-s", numero, "shell", "input", "keyevent", "KEYCODE_POWER"]
        try:
            subprocess.run(command, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de la commande POWER : {e}")

def start_application(adb_exe_path, numero, package_name):
    """
    Démarre une application sur l'appareil.

    Args:
        adb_exe_path (str): Le chemin vers l'exécutable ADB.
        numero (str): Le numéro de série de l'appareil.
        package_name (str): Le nom du package de l'application.
    """
    try:
        # Obtenir le nom complet de l'activité principale
        activity_output = subprocess.check_output(
            [adb_exe_path, "-s", numero, "shell", "cmd", "package", "resolve-activity", "--brief", package_name],
            stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW
        ).decode("utf-8").strip()

        # Extraire le nom de l'activité (dernière ligne normalement)
        activity_name = activity_output.split('\n')[-1].strip()

        # Démarrer l'application avec le nom complet de l'activité
        start_command = [
            adb_exe_path, "-s", numero, "shell", "am", "start",
            "-n", activity_name
        ]
        subprocess.run(start_command, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'obtention ou du démarrage de l'activité principale : {e}")

def stop_application(adb_exe_path, numero, package_name):
    """
    Arrête une application en cours d'exécution sur l'appareil.

    Args:
        adb_exe_path (str): Le chemin vers l'exécutable ADB.
        numero (str): Le numéro de série de l'appareil.
        package_name (str): Le nom du package de l'application.
    """
    try:
        stop_command = [adb_exe_path, "-s", numero, "shell", "am", "force-stop", package_name]
        subprocess.run(stop_command, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'arrêt de l'application {package_name} : {e}")

def is_application_running(adb_exe_path, numero, package_name):
    """
    Vérifie si une application est en cours d'exécution sur l'appareil.

    Args:
        adb_exe_path (str): Le chemin vers l'exécutable ADB.
        numero (str): Le numéro de série de l'appareil.
        package_name (str): Le nom du package de l'application.

    Returns:
        bool: True si l'application est en cours d'exécution, False sinon.
    """
    try:
        check_command = [adb_exe_path, "-s", numero, "shell", "pidof", package_name]
        output = subprocess.check_output(check_command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8").strip()
        if output:
            return True
    except subprocess.CalledProcessError:
        pass
    return False

def configure_wifi_on_casque(self, adb_exe_path, ssid, password):
    """
    Configure le Wi-Fi sur l'appareil en envoyant un broadcast.

    Args:
        adb_exe_path (str): Le chemin vers l'exécutable ADB.
        ssid (str): Le SSID du réseau Wi-Fi.
        password (str): Le mot de passe du réseau Wi-Fi.
    """
    if not ssid or not password:
        print("SSID or password is missing, cannot configure WiFi.")
        return

    try:
        set_network_command = [
            "shell", "am", "broadcast", "-a", 
            "com.yourapp.CONFIGURE_WIFI", "--es", "ssid", ssid, "--es", "password", password
        ]

        result = subprocess.run([adb_exe_path] + set_network_command, text=True, capture_output=True, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        
        if "Broadcast completed: result=0" in result.stdout:
            print("Broadcast was sent, but no changes were made. Output:", result.stdout)
        else:
            print("WiFi configuration applied successfully. Output:", result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while configuring WiFi on the casque: {e}\n{e.stderr.decode()}")

def check_battery_level(adb_exe_path, device_serial):
    """
    Vérifie le niveau de batterie de l'appareil.

    Args:
        adb_exe_path (str): Le chemin vers l'exécutable ADB.
        device_serial (str): Le numéro de série de l'appareil.

    Returns:
        int: Le niveau de batterie en pourcentage, ou -1 en cas d'erreur.
    """
    try:
        battery_info_command = [adb_exe_path, "-s", device_serial, "shell", "dumpsys", "battery"]
        output = subprocess.check_output(battery_info_command, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8")

        for line in output.split('\n'):
            if 'level' in line:
                level = int(line.split(':')[1].strip())
                return level
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la vérification du niveau de batterie : {e.output.decode('utf-8')}")
    except Exception as e:
        print(f"Erreur inattendue lors de la vérification du niveau de batterie : {e}")

    return -1
