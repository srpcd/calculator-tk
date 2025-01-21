import sqlite3
import winreg
import os


class CalculatorDataStore:
    """
    Valid databases: preferences and history.
    """
    
    def __init__(self, database: str, specified_data=None, not_use_memory=True):
        self.localappdata = os.getenv("localappdata")
        self.database = database
        
        if specified_data is None:
            if not self.localappdata:
                self.conn = sqlite3.connect(":memory:")
                self.cur = self.conn.cursor()
                self.using_memory = True
                return
            
            self.database_folder = os.path.join(self.localappdata, 'calculator-tk')
        else:
            if not not_use_memory:
                self.conn = sqlite3.connect(":memory:")
                self.cur = self.conn.cursor()
                self.using_memory = True
                return
            
            self.database_folder = specified_data.save_path
        self.using_memory = False
        os.makedirs(self.database_folder, exist_ok=True)
        self.database_file_name = os.path.join(self.database_folder, self.database + '.db')
        
        self.conn = sqlite3.connect(self.database_file_name)
        self.cur = self.conn.cursor()
    
    def add_to_history(self, operation, op_display, op_array, result, re_display, re_array):
        if self.database != 'history':
            return
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS History (
                id INTEGER PRIMARY KEY, 
                operation TEXT, 
                op_display TEXT, 
                op_array TEXT, 
                result TEXT, 
                re_display TEXT, 
                re_array TEXT, 
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        self.cur.execute("INSERT INTO History (operation, op_display, op_array, result, re_display, re_array) "
                         "VALUES (?, ?, ?, ?, ?, ?)",
                         (operation, op_display, op_array, result, re_display, re_array))
        self.conn.commit()
        
    def apply(self, btn=None):
        if btn:
            btn.config(state='disabled')
        self.conn.commit()
        
    def get_preferences(self, key):
        if self.database != 'preferences':
            return
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Preferences (
                id INTEGER PRIMARY KEY, 
                key TEXT, 
                value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        self.cur.execute("SELECT * FROM Preferences WHERE key = ?", (key,))
        return self.cur.fetchall()
        
    def set_preferences(self, key, value, id_=1):
        """
        valid keys: storehistory, darkmode
        """
        if self.database != 'preferences':
            return
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Preferences (
                id INTEGER PRIMARY KEY, 
                key TEXT, 
                value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        # self.cur.execute("DELETE FROM Preferences WHERE key = ?", (key,))
        self.cur.execute("INSERT OR REPLACE INTO Preferences (id, key, value) VALUES (?, ?, ?)", (id_, key, value))
        
    def clear_history(self, calcs, history_btn=None):
        if self.database != 'history':
            return
        self.cur.execute("DELETE FROM History")
        for frame in calcs:
            frame.destroy()
        if len(self.get_history_calculations()) == 0 and history_btn is not None:
            history_btn.config(state='disabled')
        elif len(self.get_history_calculations()) != 0 and history_btn is not None:
            history_btn.config(state='normal')
        
    def delete_from_history(self, id_, history_btn=None):
        if self.database != 'history':
            return
        self.cur.execute("DELETE FROM History WHERE id = ?", (id_,))
        
        self.cur.execute("SELECT id FROM History ORDER BY timestamp ASC;")
        rows = self.cur.fetchall()

        for new_id, row in enumerate(rows, start=1):
            if new_id != row[0]:
                self.cur.execute("UPDATE History SET id = ? WHERE id = ?", (new_id, row[0]))
        
        if len(self.get_history_calculations()) == 0 and history_btn is not None:
            history_btn.config(state='disabled')
        elif len(self.get_history_calculations()) != 0 and history_btn is not None:
            history_btn.config(state='normal')
    
    def get_history_calculations(self):
        if self.database != 'history':
            return
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS History (
                id INTEGER PRIMARY KEY, 
                operation TEXT, 
                op_display TEXT, 
                op_array TEXT, 
                result TEXT, 
                re_display TEXT, 
                re_array TEXT, 
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        self.cur.execute("SELECT * FROM history")
        content = self.cur.fetchall()
        return content
    
    def close(self):
        if hasattr(self, 'cur'):
            self.cur.close()
            del self.cur
        if hasattr(self, 'conn'):
            self.conn.close()
            del self.conn


class CalculatorRegDataStore:
    """
    This is a very important data store to specify where the files in path are stored
    """
    
    def __init__(self):
        self.default_key_path = "Software\\calculator-tk"
        self.default_value_name_version = "Version"
        self.default_value_data_version = "1.0.0"
        self.default_value_name_save_path = "SavePath"
        self.default_value_data_save_path = "%LOCALAPPDATA%\\calculator-tk"
        self.default_value_name_save_settings_flag = "SaveSettings"
        self.default_value_data_save_settings_flag = 1
        
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.default_key_path, 0, winreg.KEY_READ) as key:
                version, _ = winreg.QueryValueEx(key, "Version")
                
                if version != self.default_value_data_version:
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, self.default_key_path)
                else:
                    return
        except FileNotFoundError:
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.default_key_path) as key:
                    winreg.SetValueEx(key, self.default_value_name_version, 0, winreg.REG_SZ,
                                      self.default_value_data_version)
                    winreg.SetValueEx(key, self.default_value_name_save_path, 0, winreg.REG_SZ,
                                      self.default_value_data_save_path)
                    winreg.SetValueEx(key, self.default_value_name_save_settings_flag, 0, winreg.REG_DWORD,
                                      self.default_value_data_save_settings_flag)
            except Exception as e:
                print(e.__class__.__name__, e)
        except Exception as e:
            print(e.__class__.__name__, e)
            
    def set_save_path(self, save_path):
        if save_path.startswith(f"{os.getenv('USERPROFILE')}\\AppData\\Local"):
            save_path = save_path.replace(f"{os.getenv('USERPROFILE')}\\AppData\\Local", f"%LOCALAPPDATA%")
        
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.default_key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, self.default_value_name_save_path, 0, winreg.REG_SZ, save_path)
        except FileNotFoundError:
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.default_key_path) as key:
                    winreg.SetValueEx(key, self.default_value_name_version, 0, winreg.REG_SZ,
                                      self.default_value_data_version)
                    winreg.SetValueEx(key, self.default_value_name_save_path, 0, winreg.REG_SZ, save_path)
                    winreg.SetValueEx(key, self.default_value_name_save_settings_flag, 0, winreg.REG_DWORD,
                                      self.default_value_data_save_settings_flag)
            except Exception as e:
                print(e)
                return False
        return True
            
    def set_save_settings(self, save_settings):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.default_key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, self.default_value_name_save_settings_flag, 0, winreg.REG_DWORD, save_settings)
        except FileNotFoundError:
            try:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.default_key_path) as key:
                    winreg.SetValueEx(key, self.default_value_name_version, 0, winreg.REG_SZ,
                                      self.default_value_data_version)
                    winreg.SetValueEx(key, self.default_value_name_save_path, 0, winreg.REG_SZ,
                                      self.default_value_data_save_path)
                    winreg.SetValueEx(key, self.default_value_name_save_settings_flag, 0, winreg.REG_DWORD,
                                      save_settings)
            except Exception as e:
                print(e.__class__.__name__, e)
                return False
        return True
    
    @property
    def version(self):
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.default_key_path, 0, winreg.KEY_READ) as key:
            return winreg.QueryValueEx(key, "Version")[0]
            
    @property
    def save_path(self):
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.default_key_path, 0, winreg.KEY_READ) as key:
            return os.path.expandvars(winreg.QueryValueEx(key, "SavePath")[0])
            
    @property
    def save_settings(self):
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.default_key_path, 0, winreg.KEY_READ) as key:
            return winreg.QueryValueEx(key, "SaveSettings")[0]
