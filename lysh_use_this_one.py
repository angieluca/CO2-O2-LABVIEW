import sys
import os
from PyQt5.QtWidgets import QApplication, QPushButton, QFileDialog, QVBoxLayout, QLabel, QWidget
import numpy as np
import pandas as pd
import joblib
import logging

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class LabelGenApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.button = QPushButton('Open File Explorer', self)
        self.button.setFixedSize(200, 40)
        self.button.clicked.connect(self.openFileExplorer)
        self.label = QLabel("No file chosen", self)
        self.count_label = QLabel("", self)  # Label to display breath counts
        self.total_count_label = QLabel("", self)  # Label to display total breath count

        layout.addWidget(self.button)
        layout.addWidget(self.label)
        layout.addWidget(self.count_label)
        layout.addWidget(self.total_count_label)

        self.setLayout(layout)
        self.setWindowTitle('File Explorer')
        self.show()

    def openFileExplorer(self):
        self.label.setText("Loading...")
        self.show()

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Excel Files (*.xlsx)", options=options)
        print("\nSelected file:", fileName, "\n")

        if fileName:
            print("yay\n")
            print(type(fileName))
            converted_file = self.convert_clean(fileName)  # generate labels
            print(type(converted_file))
            # print("SUCCESS WOOO")
            # from os import startfile
            # startfile(converted_file)
            
        else:
            print("aw")
        

#         if fileName:
#             logging.info("Starting file conversion..")
#             converted_file = self.convert_clean(fileName)  # generate labels
#             logging.info("File conversion completed")
#             #self.label.setText("File should be opening :)")
#             #self.show()

#             # Open label gen file depending on os
#             if sys.platform.startswith('win'):
#                 from os import startfile
#                 startfile(converted_file)
#             elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
#                 import subprocess
#                 subprocess.Popen(['xdg-open', converted_file])

    def convert_clean(self, new_path_type2):
        try:
            # Read excel file using pandas and store in DataFrame (like a table; each column = field, each row = record)
            new_df_type2 = pd.read_excel(new_path_type2)

            # Full column headers
            full_column_headers = ['Sample', 'CPU Date', 'CPU Time', 'Site Time', 'Period Time', 'Protocol Type', 'Storage ID', 'First Beat ID', 'Last Beat ID', 'Ti (msec)', 'Te (msec)', 'PIF', 'PEF', 'TV', 'EV', 'RT (msec)', 'MV', 'P (msec)', 'f (bpm)', 'EIP (msec)', 'EEP (msec)', 'Penh', 'EF50', 'RH', 'Tbox', 'Tbody', 'Sr', 'Phase']

            # Get ML column headers
            column_headers = ['Ti (msec)', 'Te (msec)', 'PIF', 'PEF', 'TV', 'EV', 'RT (msec)', 'MV', 'P (msec)', 'f (bpm)', 'EIP (msec)', 'EEP (msec)', 'Penh', 'EF50', 'Sr', 'Phase']

            # Extract features that ML model will use to make predictions
            new_features_type2 = new_df_type2[column_headers]

            # Convert to numpy array
            new_data_train_type2 = new_features_type2.to_numpy()

            # Make predictions on the data
            model_path = resource_path('best_pleth_ml_model_type2.pkl')
            loaded_model_type2 = joblib.load(model_path)
            pred_type2 = loaded_model_type2.predict(new_data_train_type2)

            # Create a new column to store the generated labels
            new_df_type2["Generated Labels"] = pred_type2

            # Save predicted labels to 'generatelabeltest.npy' file
            np.save('generatelabeltest.npy', pred_type2)

            # Load the generated labels
            generated_labels = np.load('generatelabeltest.npy')

            # Define label descriptions
            label_descriptions = {
                0: "Normal / Quiet Breath",
                1: "Sigh breath",
                2: "Sniffing breath",
                3: "Random Apnea",
                4: "Type II Apnea"
            }

            # Count the occurrences of each label
            label_counts = np.unique(generated_labels, return_counts=True)

            # Initialize total breath count
            total_breath_count = 0

            # Create a string to store the breath counts
            count_text = ""

            # Print the counts with descriptions
            for label, count in zip(label_counts[0], label_counts[1]):
                description = label_descriptions[int(label)]
                count_text += f"{description} count ({int(label)}): {count}\n"
                # Increment total breath count
                total_breath_count += count

            # Display the breath counts on the label
            self.count_label.setText(count_text)

            # Display the total breath count on the label
            self.total_count_label.setText(f"Total breath count: {total_breath_count}")

            # Convert and export DataFrame to Excel with all columns
            excel_file_path = new_path_type2[:-5] + "_LABELGEN.xlsx"  # change new file name
            #print("\nSuccess! New labeled file:", excel_file_path, "\n")
            new_df_type2.to_excel(excel_file_path, index=False)
            return excel_file_path
        
        except FileNotFoundError as e:
            logging.exception("File not found")

        except Exception as e:
            logging.exception("An error occured during file conversion:")


if __name__ == '__main__':
    logging.basicConfig(filename='labelgen.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    app = QApplication(sys.argv)
    file_explorer = LabelGenApp()
    sys.exit(app.exec_())

print("hello")