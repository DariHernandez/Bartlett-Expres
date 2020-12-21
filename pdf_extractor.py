# Import the software to read the file
import pdfplumber, os

class extract_pdfs (): 
    """ Extract information from PDF files in specific folder"""

    def __init__ (self, folder): 
        """ Constructor of the class. Read all pdf files and return formated data"""

        self.__all_data_files = []

        # Loop for each file inside the folder
        for file_name in os.listdir (folder): 

            # Get full name of the file
            pdf_file = os.path.join (folder, file_name)

            # Try to extract curent file
            try: 
                # Extract data for the current file
                file_data = self.extract_file(pdf_file)

                # Format data for the current file
                formated_data = self.get_formated_file(file_data)

                # add current row of data to main list of data
                self.__all_data_files += formated_data
            
            # Ctach an error to extract file
            except: 
                print ("Error to extract {} file. \
                    The file does not have the structure of an invoice.".format(file_name))


    def get_all_data_files (self):
        """ Get all data from all files"""

        return self.__all_data_files


    def extract_file (self, file): 
        """ Extract information from specific pdf file"""

        file_name = os.path.basename (file)
        print ("Extracting information from the file %s" % (file_name))

        # local variables used to store information temporarily
        invoiceNumber = ''
        dateInvoice = ''
        clientReference = ''
        charges = []
        invoiceTotal = ''

        # extract information from each file
        with pdfplumber.open(file) as pdf:

            # Select page
            first_page = pdf.pages[0]

            # group all text from PDF file
            group_text = first_page.extract_text()

            # split text for each line
            array_text_list = group_text.split('\n')

            # Read each line of the resulting list
            for line_text in array_text_list:

                # The invoice number is always on line 1 of the text.
                # Check if the current line is line 1.
                if array_text_list.index(line_text) == 0: 

                    # Check the first text to validate that the pdf document is an invoice
                    if line_text[:8].strip().upper() != "INVOICE":
                        # Rise an error
                        raise Exception ("Error to extract file")


                    # save only the invoice number
                    invoiceNumber += line_text[8:]
                
                # The date and the client are always on line 2. 
                # Check if the current line is line 2.
                elif array_text_list.index(line_text) == 2: 

                    # save as date, all the text after the word "DATE"
                    dateInvoice += line_text[line_text.index('DATE')+4:]

                    # save as client, all the text that is before the word "date"
                    clientReference += line_text[:line_text.index('DATE')]


                # charges are always found between the lines: "DESCRIPTION CHARGES IN USD" and "TOTAL CHARGES"
                # Check if the current line is "DESCRIPTION CHARGES IN USD"
                if line_text == ("DESCRIPTION CHARGES IN USD"):

                    # save the current line number in a local variable
                    current_line = array_text_list.index (line_text)

                    # Make a loop for save each charge
                    while True:

                        # increment the local variable
                        current_line += 1

                        # read the next line
                        line = array_text_list[current_line]

                        # if the next line is "TOTAL CHARGES", then finish the loop,
                        #   else save the chargues line
                        if line == "TOTAL CHARGES":
                            break
                        else: 
                            charges.append (line)

                if "TOTAL USD" in line_text: 
                    invoiceTotal = line_text[10:]
        
        # return a dicionatry of the psd data
        return {
            "invoiceNumber": invoiceNumber, 
            "dateInvoice": dateInvoice, 
            "clientReference": clientReference,
            "charges": charges,
            "invoiceTotal": invoiceTotal
        }
             
    def get_formated_file (self, data): 
        """return formated data from specific data file """

        # Empty dicionary to save data to return
        formated_data = []

        # Make a loop for each charge
        for charge in data["charges"]: 

            # Empty list to save the formated current row
            formated_row = []

            # save information to the list, in the correct order
            formated_row.append ("Freighters")
            formated_row.append (data["invoiceNumber"])
            formated_row.append (data["dateInvoice"])
            formated_row.append (data["clientReference"])
            formated_row.append (data["invoiceTotal"])
            
            # SEPARATE TEXT AND PRICE CORRESPONDING TO THE CHARGE

            # control variables to separate the "charge" and the "amount charge"
            position = 0
            amount_start = 0

            # if the charge includes a date, take the following position character as variable amount_start
            if charge.rfind ('/'): 
                amount_start = charge.rfind ('/')+2


            # make a loop for each character, within the text corresponding to the current charge
            for index in range (amount_start, len(list(charge))): 

                # if the current character is a number, set the position of the character as "position" variable
                if str(list(charge)[index]).isdigit(): 
                    position = index
                    break

            # the name of the charge, is a substring, which runs from the beginning to before the price
            charge_amount = charge[position:]

            # the price of the charge, is a substring, from the character where it was detected that the amount starts, to the end of the string
            charge_name = charge[:position]
        
            # Save name and amount in the formated row
            formated_row.append (charge_amount)
            formated_row.append (charge_name)
            
            # Add current row to the list of the formated data
            formated_data.append (formated_row)

        return formated_data
            
            


    


