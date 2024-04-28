import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector

class CloudKitchen:
    def __init__(self, root):
        self.root = root
        self.root.title("Cloud Kitchen DBMS")
        self.root.geometry("800x600")

        # Database Connection
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="cloudkitchen_database"
        )
        self.cursor = self.db.cursor()

        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Treeview", font=("Helvetica", 11))

        # Sign In Page
        self.sign_in_frame = tk.Frame(root)
        self.sign_in_frame.pack(pady=50)

        self.admin_label = tk.Label(self.sign_in_frame, text="Admin Sign In", font=("Helvetica", 16))
        self.admin_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.username_label = tk.Label(self.sign_in_frame, text="Username:", font=("Helvetica", 14))
        self.username_label.grid(row=1, column=0)
        self.username_entry = tk.Entry(self.sign_in_frame, font=("Helvetica", 14))
        self.username_entry.grid(row=1, column=1)

        self.password_label = tk.Label(self.sign_in_frame, text="Password:", font=("Helvetica", 14))
        self.password_label.grid(row=2, column=0)
        self.password_entry = tk.Entry(self.sign_in_frame, show="*", font=("Helvetica", 14))
        self.password_entry.grid(row=2, column=1)

        self.sign_in_button = tk.Button(self.sign_in_frame, text="Sign In", command=self.admin_sign_in, font=("Helvetica", 14))
        self.sign_in_button.grid(row=3, column=0, columnspan=2, pady=10)

    def admin_sign_in(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # You should implement your authentication logic here
        # For simplicity, let's assume username and password are correct
        if username == "admin" and password == "password":
            self.sign_in_frame.destroy()
            self.admin_panel()
        else:
            # Display an error message for incorrect credentials
            messagebox.showerror("Error", "Invalid username or password")

    def admin_panel(self):
        self.admin_panel_frame = tk.Frame(self.root)
        self.admin_panel_frame.pack(pady=20)

        # Buttons for Database Management Functions
        buttons = [
            ("View Tables", self.view_tables),
            ("Add Record", self.add_record),
            ("Delete Record", self.delete_record),
            ("Edit Record", self.edit_record),
            ("Add Table", self.add_table),
            ("Delete Table", self.delete_table),
            ("Logout", self.logout)
        ]

        row = 0
        for text, command in buttons:
            button = tk.Button(self.admin_panel_frame, text=text, command=command, font=("Helvetica", 14))
            button.grid(row=row, column=0, pady=5)
            row += 1

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if confirm:
            self.admin_panel_frame.destroy()
            self.sign_in_frame.pack(pady=50)  # Re-pack the sign-in frame to display it again

    def view_tables(self):
        self.view_tables_window = tk.Toplevel(self.root)
        self.view_tables_window.title("View Tables")

        self.tables_notebook = ttk.Notebook(self.view_tables_window)
        self.tables_notebook.pack(fill="both", expand=True)

        # Retrieve tables data from the database and create tabs for each table
        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()
        for table in tables:
            table_name = table[0]
            tab_frame = tk.Frame(self.tables_notebook)
            self.tables_notebook.add(tab_frame, text=table_name)

            try:
                # Fetch column names from the table
                self.cursor.execute(f"SHOW COLUMNS FROM {table_name}")
                columns = self.cursor.fetchall()

                # Create a Treeview widget to display records
                treeview = ttk.Treeview(tab_frame)
                treeview["columns"] = [f"col{i}" for i in range(len(columns))]
                for i, col in enumerate(columns):
                    treeview.column(f"col{i}", width=100, anchor="w")
                    treeview.heading(f"col{i}", text=col[0])  # Use column name as header

                # Fetch records from the table
                self.cursor.execute(f"SELECT * FROM {table_name}")
                records = self.cursor.fetchall()

                # Insert records into the Treeview
                for record in records:
                    treeview.insert("", "end", values=record)
            
                # Add Treeview to the tab frame
                treeview.pack(fill="both", expand=True)
            except Exception as e:
                messagebox.showerror("Error", f"Error viewing table '{table_name}': {str(e)}")

    def add_record(self):
        table_name = simpledialog.askstring("Add Record", "Enter Table Name:")
        if table_name:
            # Fetch table columns
            self.cursor.execute(f"DESCRIBE {table_name}")
            columns = [column[0] for column in self.cursor.fetchall()]

            record_values = {}
            for column in columns:
                value = simpledialog.askstring(f"Add Record", f"Enter value for {column}:")
                record_values[column] = value

            # Construct the query
            columns_str = ", ".join(record_values.keys())
            values_str = ", ".join([f"'{value}'" for value in record_values.values()])
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"

            try:
                self.cursor.execute(query)
                self.db.commit()
                messagebox.showinfo("Success", "Record added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error adding record: {str(e)}")

    def delete_record(self):
        table_name = simpledialog.askstring("Delete Record", "Enter Table Name:")
        if table_name:
            # Fetch the primary key field (assuming it's named 'ID')
            self.cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
            primary_key_info = self.cursor.fetchone()
            if primary_key_info:
                primary_key_field = primary_key_info[4]

                record_id = simpledialog.askinteger("Delete Record", f"Enter {primary_key_field} of the record to delete:")
                if record_id is not None:
                    confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to delete {primary_key_field} {record_id} from table '{table_name}'?")
                    if confirm:
                        try:
                            query = f"DELETE FROM {table_name} WHERE {primary_key_field}={record_id}"
                            self.cursor.execute(query)
                            self.db.commit()
                            messagebox.showinfo("Success", "Record deleted successfully!")
                        except Exception as e:
                            messagebox.showerror("Error", f"Error deleting record: {str(e)}")
            else:
                messagebox.showerror("Error", "Primary key field not found. Please check the table structure.")

    def edit_record(self):
        table_name = simpledialog.askstring("Edit Record", "Enter Table Name:")
        if table_name:
            # Fetch the primary key field dynamically
            self.cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
            primary_key_info = self.cursor.fetchone()
            if primary_key_info:
                primary_key_field = primary_key_info[4]

                # Fetch records from the table
                self.cursor.execute(f"SELECT * FROM {table_name}")
                records = self.cursor.fetchall()
                if records:
                    # Display the records for the user to select for editing
                    edit_record_window = tk.Toplevel(self.root)
                    edit_record_window.title("Select Record to Edit")

                    edit_record_frame = tk.Frame(edit_record_window)
                    edit_record_frame.pack()

                    # Create a Treeview widget to display records
                    treeview = ttk.Treeview(edit_record_frame)
                    treeview["columns"] = [field[0] for field in self.cursor.description]
                    for field in self.cursor.description:
                        treeview.column(field[0], width=100, anchor="w")
                        treeview.heading(field[0], text=field[0])

                    # Insert records into the Treeview
                    for record in records:
                        treeview.insert("", "end", values=record)
                
                    # Add Treeview to the frame
                    treeview.pack(fill="both", expand=True)

                    # Function to edit selected record
                    def edit_selected_record():
                        selected_item = treeview.selection()
                        if selected_item:
                            record_id = treeview.item(selected_item)["values"][0]  # Assuming ID is the first column
                            # Prompt user to enter new values for each field
                            new_values = {}
                            for field in treeview["columns"]:
                                new_value = simpledialog.askstring("Edit Record", f"Enter new value for {field}:")
                                new_values[field] = new_value

                            # Construct the UPDATE query
                            set_values = ", ".join([f"{field}='{new_values[field]}'" for field in new_values])
                            query = f"UPDATE {table_name} SET {set_values} WHERE {primary_key_field}={record_id}"
                        
                            try:
                                self.cursor.execute(query)
                                self.db.commit()
                                messagebox.showinfo("Success", "Record updated successfully!")
                                edit_record_window.destroy()  # Close the window after successful edit
                            except Exception as e:
                                messagebox.showerror("Error", f"Error updating record: {str(e)}")
                        else:
                            messagebox.showerror("Error", "Please select a record to edit.")

                    # Button to edit selected record
                    edit_button = tk.Button(edit_record_frame, text="Edit Selected Record", command=edit_selected_record, font=("Helvetica", 14))
                    edit_button.pack(pady=10)
                else:
                    messagebox.showinfo("Information", "No records found in the table.")
            else:
                messagebox.showerror("Error", "Primary key field not found. Please check the table structure.")

    def add_table(self):
        table_name = simpledialog.askstring("Add Table", "Enter Table Name:")
        if table_name:
            fields = simpledialog.askstring("Add Table", "Enter comma-separated fields with types (e.g., Field1 INT, Field2 VARCHAR(50)):")
            if fields:
                try:
                    query = f"CREATE TABLE {table_name} ({fields})"
                    self.cursor.execute(query)
                    self.db.commit()
                    messagebox.showinfo("Success", f"Table '{table_name}' created successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Error creating table: {str(e)}")

    def delete_table(self):
        table_name = simpledialog.askstring("Delete Table", "Enter Table Name:")
        if table_name:
            try:
                confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to delete table '{table_name}'?")
                if confirm:
                    self.cursor.execute(f"DROP TABLE {table_name}")
                    self.db.commit()
                    messagebox.showinfo("Success", f"Table '{table_name}' deleted successfully!")
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Error deleting table: {e.msg}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CloudKitchen(root)
    root.mainloop()
