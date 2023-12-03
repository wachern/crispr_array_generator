import crispr_array_generator.constants as cn
import openpyxl
from openpyxl import load_workbook
from openpyxl import Workbook


class Array(object):
    def extract_excel_data(excel_file):
        """
        Exracts all data from an excel file and isolates DNA
        components
        Args:
            string: name of excel file listing guide RNAs in 5' 
            to 3' format
        Returns:
            array: all DNA components listed in the input excel file
        """
        
        excel_file = excel_file+".xlsx"
        workbook = load_workbook(excel_file)
        exceldata = []
        grnas = []
        sheet = workbook.active
        # Changing the layout of each excel cell value 
        for value in sheet.iter_rows(values_only=True):
            value = str(value)
            value = value.replace("'" , "")
            value = value.replace("," , "")
            value = value.replace("(" , "")
            value = value.replace(")" , "")
            exceldata.append(value)
        # Isolating DNA values
        for input in exceldata:
            valid_dna = all(i in cn.VALID_DNA for i in input)
            if valid_dna==True:
                grnas.append(input)
        return grnas

    def get_reverse_complement(dna):
        """
        Converts a 5' to 3' DNA string into its 3' to 5' reverse 
        complement
        Args:
            string: DNA to be converted
        Returns:
            string: reverse complement of input DNA
        """
        dna_comp = [cn.BASE_PAIRS[base] for base in dna]
        dna_rev_comp = dna_comp[::-1]
        return ''.join(dna_rev_comp)

    def check_grna(excel_file):
        """
        Takes gRNAs listed in an excel file and checks them for 
        self-targeting or length errors
        Args:
            string: name of excel file listing guide RNAs in 5' 
            to 3' format
        Returns:
            file: excel file listing processed gRNAs and errors 
            if found
        """
        grnas = Array.extract_excel_data(excel_file)
        new_grnas = []
        cell = 0
        # Creating the output workbook object
        excel_output = Workbook()
        sheet_1 = excel_output.create_sheet("gRNAcheck")
        if 'Sheet' in excel_output.sheetnames:
            excel_output.remove(excel_output['Sheet'])
        # Creating headers
        sheet_1.cell(row=1 , column=1).value = "gRNAs"
        sheet_1.cell(row=1 , column=2).value = "self-target error (TTC cut site within gRNA)"
        sheet_1.cell(row=1 , column=3).value = "length error (>24 nucleotides)"
        sheet_1.cell(row=1 , column=4).value = "length error (<20 nucleotides)"
        for grna in grnas:
            cell = cell + 1
            #Removing CRISPR cut site within gRNA if present
            grna = grna.removeprefix("TTC")
            grna = grna.removeprefix("ttc")
            #Checking if any TTC left within gRNA
            if 'ttc' in grna or 'TTC' in grna:
                sheet_1.cell(row=cell+1 , column=2).value = "X"
            #Checking gRNA length
            if len(grna) > 24:
                sheet_1.cell(row=cell+1 , column=3).vale = "X"
            if len(grna) < 20:
                c3 = sheet_1.cell(row=cell+1 , column=4).value = "X"
            new_grnas.append(grna)
            #Putting new gRNAs into the output excel file
            c3 = sheet_1.cell(row=cell+1 , column=1)
            c3.value = grna
        excel_output.save('grnacheck.xlsx')
        return(new_grnas)

    def get_array(excel_file):
        """
        Generates ready-to-order oligos from input gRNAs listed on an 
        excel file
        Args:
            string: name of excel file listing guide RNAs in 5' to 3'
            format 
        Returns:
            excel file listing ready-to-order oligos for each set of 
            gRNAs and any errors if present
        """
        revcomp_grnas = []
        new_grnas = Array.check_grna(excel_file)
        excel_output = load_workbook("grnacheck.xlsx")
        sheet_2 = excel_output.create_sheet("Array")
        sheet_2.cell(row=1 , column=2).value = "Full array fwd:"
        sheet_2.cell(row=1 , column=3).value = "Full array rev:"
        sheet_2.cell(row=1 , column=5).value = "Errors:"
        sheet_2.cell(row=4 , column=1).value = "gRNA #:"
        sheet_2.cell(row=4 , column=2).value = "Fwd oligos:"
        sheet_2.cell(row=4 , column=3).value = "Rev oligos:"
        number = len(new_grnas)
        for value in range(1, number+1):
            s2.cell(row=value + 4, column=1).value = value
        if number > 9:
            sheet_2.cell(row=2, column=5).value = "More than 9 gRNAs were identified. Please input 9 or fewer gRNAs per array."
        #Creating array oligos and inserting them into "grnacheck.xlsx"
        for grna in new_grnas:
            grnarev = Array.get_reverse_complement(grna)
            revcomp_grnas.append(grnarev)
        if number>=1 and number<=9:
            F1 = sheet_2.cell(row=5 , column=2).value = "CCCTAAATAATTTCTACTGTTGTAGAT" + new_grnas[0]
            if number==1:
                R11 = sheet_2.cell(row=5 , column=3).value = "CGTT" + revcomp_grnas[0] + "ATCTACAACAGTAGAAATTATTT"
                sheet_2.cell(row=2 , column=2).value = F1
                sheet_2.cell(row=2 , column=3).value = R11
        if number>=2 and number<=9:
            R1 = sheet_2.cell(row=5 , column=3).value = "GCCA" + revcomp_grnas[0] + "ATCTACAACAGTAGAAATTATTT"
            if number==2:
                F22 = sheet_2.cell(row=6 , column=2).value = "TGGCAAATAATTTCTACTGTTGTAGAT" + new_grnas[1]
                R22 = sheet_2.cell(row=6 , column=3).value = "CGTT" + revcomp_grnas[1] + "ATCTACAACAGTAGAAATTATTT"
                sheet_2.cell(row=2 , column=2).value = F1 + F22
                sheet_2.cell(row=2 , column=3).value = R22 + R1
        if number>=3 and number<=9:
            F2 = sheet_2.cell(row=6 , column=2).value = "TGGCAAATAATTTCTACTGTTGTAGAT" + new_grnas[1] + "TTCT"
            R2 = sheet_2.cell(row=6 , column=3).value = revcomp_grnas[1] + "ATCTACAACAGTAGAAATTATTT"
            F3 = sheet_2.cell(row=7 , column=2).value = "AAATAATTTCTACTGTTGTAGAT" + new_grnas[2]
            if number==3:
                R33 = sheet_2.cell(row=7 , column=3).value = "CGTT" + revcomp_grnas[2] + "ATCTACAACAGTAGAAATTATTTAGAA"
                sheet_2.cell(row=2 , column=2).value = F1 + F2 + F3
                sheet_2.cell(row=2 , column=3).value = R33 + R2 + R1
        if number>=4 and number<=9:
            R3 = sheet_2.cell(row=7 , column=3).value = "ATTG" + revcomp_grnas[2] + "ATCTACAACAGTAGAAATTATTTAGAA"
            if number==4:
                F44 = sheet_2.cell(row=8 , column=2).value = "CAATAAATAATTTCTACTGTTGTAGAT" + new_grnas[3]
                R44 = sheet_2.cell(row=8 , column=3).value = "CGTT" + revcomp_grnas[3] + "ATCTACAACAGTAGAAATTATTT"
                sheet_2.cell(row=2 , column=2).value = F1 + F2 + F3 + F44
                sheet_2.cell(row=2 , column=3).value = R44 + R3 + R2 + R1
        if number>=5 and number<=9:
            F4 = sheet_2.cell(row=8 , column=2).value = "CAATAAATAATTTCTACTGTTGTAGAT" + new_grnas[3] + "TATG"
            R4 = sheet_2.cell(row=8 , column=3).value =  revcomp_grnas[3] + "ATCTACAACAGTAGAAATTATTT"
            F5 = sheet_2.cell(row=9 , column=2).value = "AAATAATTTCTACTGTTGTAGAT" + new_grnas[4]
            if number==5:
                R55 = sheet_2.cell(row=9, column=3).value = "CGTT" + revcomp_grnas[4] + "ATCTACAACAGTAGAAATTATTTCATA"
                sheet_2.cell(row=2 , column=2).value = F1 + F2 + F3 + F4 + F5
                sheet_2.cell(row=2 , column=3).value = R55 + R4 + R3 + R2 + R1
        if number>=6 and number<=9:
            R5 = sheet_2.cell(row=9 , column=3).value = "TTCT" + revcomp_grnas[4] + "ATCTACAACAGTAGAAATTATTTCATA"
            if number==6:
                F66 = sheet_2.cell(row=10 , column=2).value = "AGAAAAATAATTTCTACTGTTGTAGAT" + new_grnas[5]
                R66 = sheet_2.cell(row=10 , column=3).value = "CGTT" + revcomp_grnas[5] + "ATCTACAACAGTAGAAATTATTT"
                sheet_2.cell(row=2 , column=2).value = F1 + F2 + F3 + F4 + F5 + F66
                sheet_2.cell(row=2 , column=3).value = R66 + R5 + R4 + R3 + R2 + R1
        if number>=7 and number<=9:
            F6 = sheet_2.cell(row=10 , column=2).value = "AGAAAAATAATTTCTACTGTTGTAGAT" + new_grnas[5] + "TACA"
            R6 = sheet_2.cell(row=10 , column=3).value = revcomp_grnas[5] + "ATCTACAACAGTAGAAATTATTT"
            F7 = sheet_2.cell(row=11 , column=2).value = "AAATAATTTCTACTGTTGTAGAT" + new_grnas[6]
            if number==7:
                R77 = sheet_2.cell(row=11 , column=3).value = "CGTT" + revcomp_grnas[6] + "ATCTACAACAGTAGAAATTATTTTGTA"
                sheet_2.cell(row=2 , column=2).value = F1 + F2 + F3 + F4 + F5 + F6 + F7
                sheet_2.cell(row=2 , column=3).value = R77 + R6 + R5 + R4 + R3 + R2 + R1
        if number>=8 and number<=9:
            R7 = sheet_2.cell(row=11, column=3).value = "CAGC" + revcomp_grnas[6] + "ATCTACAACAGTAGAAATTATTTTGTA"
            if number==8:
                F88 = sheet_2.cell(row=12 , column=2).value = "GCTGAAATAATTTCTACTGTTGTAGAT" + new_grnas[7]
                R88 = sheet_2.cell(row=12 , column=3).value = "CGTT" + revcomp_grnas[7] + "ATCTACAACAGTAGAAATTATTT"
                sheet_2.cell(row=2 , column=2).value = F1 + F2 + F3 + F4 + F5 + F6 + F7 + F88
                sheet_2.cell(row=2 , column=3).value = R88 + R7 + R6 + R5 + R4 + R3 + R2 + R1
        if number==9:
            F8 = sheet_2.cell(row=12 , column=2).value = "GCTGAAATAATTTCTACTGTTGTAGAT" + new_grnas[7] + "GAGT"
            R8 = sheet_2.cell(row=12 , column=3).value = revcomp_grnas[7] + "ATCTACAACAGTAGAAATTATTT"
            F9 = sheet_2.cell(row=13 , column=2).value = "AAATAATTTCTACTGTTGTAGAT" + new_grnas[8]
            R9 = sheet_2.cell(row=13 , column=2).value = "CGTT" + revcomp_grnas[8] + "ATCTACAACAGTAGAAATTATTTACTC"
			sheet_2.cell(row=2 , column=2).value = F1 + F2 + F3 + F4 + F5 + F6 + F7 + F8 + F9
            sheet_2.cell(row=2 , column=3).value = R9 + R8 + R7 + R6 + R5 + R4 + R3 + R2 + R1
        excel_output.save('grnacheck.xlsx')

