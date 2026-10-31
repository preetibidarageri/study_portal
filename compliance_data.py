from __future__ import unicode_literals
from frappe import _
import frappe
from frappe.model.document import Document
from frappe.desk.form.load import get_attachments
from frappe.utils.print_format import read_multi_pdf
from pathlib import Path
from io import BytesIO, StringIO
from openpyxl.styles import Border, Side
from datetime import datetime, timedelta
import calendar
import pdfkit
from openpyxl import Workbook, load_workbook
from openpyxl.formula import tokenizer
import json
from bs4 import BeautifulSoup

from frappe.utils.pdf import get_pdf
from pypdf import PdfWriter, PdfReader, PdfMerger
from pypdf.generic import RectangleObject
import re
from frappe.utils.file_manager import get_file, save_url, get_file_path

class ComplianceData(Document):

	@frappe.whitelist()
	def on_update(self):
		if self.pf_receipt:
			import tabula
			cd_doc = frappe.get_doc("Compliance Data", str(self.name))
			tables = tabula.read_pdf(get_file_path(cd_doc.pf_receipt), pages='1', multiple_tables=True)

			for table in tables:
				dt = table.to_csv()
				if dt.startswith(",TRRN No :,"):
					dt = dt.split(",TRRN No :,")[1]
					rows = dt.split("\n")
					frappe.db.set_value("Compliance Data", self.name, 'trrn_number', rows[0])

				if ",Total Amount (Rs) :," in dt:
					dt = dt.split(",Total Amount (Rs) :,")[1]
					rows = dt.split("\n")
					number_string = rows[0].replace('"', '').replace(',', '')
					frappe.db.set_value("Compliance Data", self.name, 'pf_receipt_amount', number_string)

				if ",Payment Date :," in dt:
					dt = dt.split(",Payment Date :,")[1]
					rows = dt.split("\n")
					parsed_date = datetime.strptime(rows[0], '%d-%b-%Y')
					formatted_date = parsed_date.strftime('%Y-%m-%d')
					frappe.db.set_value("Compliance Data", self.name, 'pf_receipt_date', str(formatted_date))

	@frappe.whitelist()
	def extract_pdf_data(self):
		date_string = self.month_year
		date_parts = date_string.split('-')
		month = date_parts[0]
		year = date_parts[1]
		final_month = month[:3]
		columns, result = get_report_data(month,year,self.branch,self.company)

		'''
		as per saloni-Hr this commented
		
		if self.branch == "Charanka_GIPCL":
			sub_branches = ["GIPCL_Plot 1","GIPCL_Plot 3"]
			columns = []
			result = []
			for branch in sub_branches:
				columns_lst, data_lsts = get_report_data(month,year,branch,self.company)
				# data +=data_lsts
				result.extend(data_lsts)
				columns=columns_lst
		else:
			columns, result = get_report_data(month,year,branch,self.company)
		'''

		# report_data = frappe.get_doc('Report', 'Employee Salary Register')
		uan_list = []
		# columns, result = report_data.run_query_report(filters={'month': final_month, 'year': year, 'branch': self.branch, 'company': self.company}, user=frappe.session.user)

		for d in result[:-1]:
			if isinstance(d, dict):
				uan_list.append(d["uan"])
		parts = []
		attach_list = get_attachments(self.doctype, self.name)
		import tabula
		import re
		tables = tabula.read_pdf(get_file_path(self.pf_ecr), pages='all', multiple_tables=True)		
		selected_rows = []
		for table in tables:
			dt = table.to_csv()
			
			lines = dt.split('\n')
			
			for line in lines:
				# Split the line by comma
				parts = line.split(',')
				# frappe.msgprint(str(parts))

				if len(parts) > 1 and parts[1].strip().isdigit():
					selected_rows.append(parts[1:])


		final_list=[]
		for i in selected_rows:
			if i[1] in uan_list:
				if len(i)-1 == 14:
					refunds = i[13].split(".")[0]
					ncp_days_cr = i[13].split(".")[1]
				elif len(i)-1 == 15:
					refunds = i[14].split(".")[0]
					ncp_days_cr = i[14].split(".")[1]
				else :
					frappe.throw("In PDF NCP Days Not found at perticuler column")

				'''d = {
					# this above condition for list len are coming 14 - 15 sometime added on 9-dec-25

					"uan": i[1],
					"gross": i[4],
					"epf": i[5],
					"eps": i[7],
					"edli": i[8],
					"refunds": i[13].split(".")[0],
					"is_abry": 0,
					"ee_cr": i[10],
					"eps_cr": i[11].split()[0],
					"er_cr": i[11].split()[1],
					"ncp_days_cr": i[13].split(".")[1]
				}'''

				d = {
					"uan": i[1],
					"gross": i[4],
					"epf": i[5],
					"eps": i[7],
					"edli": i[8],
					"refunds": refunds,
					"is_abry": 0,
					"ee_cr": i[10],
					"eps_cr": i[11].split()[0],
					"er_cr": i[11].split()[1],
					"ncp_days_cr": ncp_days_cr
				}
				final_list.append(d)
		return final_list
	



		# frappe.msgprint(str(final_list))
		# frappe.msgprint(str(parts[1:]))
		# frappe.msgprint(f"\nTotal rows extracted: {len(employee_data)}")


		'''data_dict = {}
		import re
		for table in tables:
			dt = table.to_csv()
			if dt.startswith(",Sl. No.,") and "EE Share,," in dt:
				dt = dt.split("EE Share,,")[1]

				rows = dt.split("\n")
				for row in rows:
					cols = row.split(",")
					if cols and any(cols):
						if cols[2].endswith(".0"):
							cols[2] = cols[2][:-2]
					if row.strip().endswith("N.A."):
						row = re.sub(r'(?!(([^\"]*\"){2})*[^\"]*$),', '', row)
						data_dict[cols[2]] = row.replace('"', '').split(",")

		frappe.msgprint(str(data_dict))'''

			
			
		

		return
		selected_rows = []
		for key in data_dict:
			d = {
				"uan": key,
				"gross": data_dict[key][5],
				"epf": data_dict[key][6],
				"eps": data_dict[key][7],
				"edli": data_dict[key][8],
				"refunds": data_dict[key][13],
				"is_abry": 0,
				"ee_cr": data_dict[key][9],
				"eps_cr": data_dict[key][10],
				"er_cr": data_dict[key][11],
				"ncp_days_cr": data_dict[key][12]
			}
			if data_dict[key][14] == "ABRY":
				d["is_abry"] = 1
			if key in uan_list:
				selected_rows.append(d)
		return selected_rows

	def extract_pdf_data2(self):
		pdfFileObj = open('US_Declaration.pdf', 'rb')
		pdf_reader = PdfReader(pdfFileObj)
		print(len(pdf_reader.pages))
		first_page = pdf_reader.pages[0]
		pdf_writer = PdfWriter()
		pdf_writer.add_page(first_page)
		pdf_output = open("Some_New_Doc.pdf", "wb")
		pdf_writer.write(pdf_output)
		with BytesIO() as bytes_stream:
			pdf_writer.write(bytes_stream)
		pdfFileObj.close()

	def merge_pdf(self):
		merger = PdfMerger()
		input1 = open("document1.pdf", "rb")
		input2 = open("document2.pdf", "rb")
		input3 = open("document3.pdf", "rb")
		merger.append(fileobj=input1, pages=(0, 3))
		merger.merge(position=2, fileobj=input2, pages=(0, 1))
		merger.append(input3)
		merger.add_metadata({"/Author": "Martin", "/Producer": "Libre Writer"})
		output = open("document-output.pdf", "wb")
		merger.write(output)
		merger.close()
		output.close()

def watermark(content_pdf: Path, stamp_pdf: Path, pdf_result: Path, page_indices: None):
	reader = PdfReader(content_pdf)
	if page_indices == "ALL":
		page_indices = list(range(0, len(reader.pages)))
	writer = PdfWriter()
	for index in page_indices:
		content_page = reader.pages[index]
		mediabox = content_page.mediabox
		reader_stamp = PdfReader(stamp_pdf)
		image_page = reader_stamp.pages[0]
		image_page.merge_page(content_page)
		image_page.mediabox = mediabox
		writer.add_page(image_page)
	with open(pdf_result, "wb") as fp:
		writer.write(fp)



def create_json_gz_file(data, dt, dn):
	# Storing data in CSV file causes information loss
	# Reports like P&L Statement were completely unsuable because of this
	json_filename = "{}.json.gz".format(
		frappe.utils.data.format_datetime(frappe.utils.now(), "Y-m-d-H:M")
	)
	encoded_content = frappe.safe_encode(frappe.as_json(data))
	compressed_content = gzip_compress(encoded_content)

	# Call save() file function to upload and attach the file
	_file = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": json_filename,
			"attached_to_doctype": dt,
			"attached_to_name": dn,
			"content": compressed_content,
			"is_private": 1,
		}
	)
	_file.save(ignore_permissions=True)


@frappe.whitelist()
def download_attachment(data, file_name):
	frappe.local.response.filename = file_name[:-3]
	frappe.local.response.filecontent = data
	frappe.local.response.type = "binary"

@frappe.whitelist()
def download_file(file_url):
	file_doc = frappe.get_doc("File", {"file_url": file_url})
	file_doc.check_permission("read")
	path = os.path.join(get_files_path(), os.path.basename(file_url))
	with open(path, "rb") as fileobj:
		filedata = fileobj.read()
	frappe.local.response.filename = os.path.basename(file_url)
	frappe.local.response.filecontent = filedata
	frappe.local.response.type = "download"

@frappe.whitelist()
def add_attachments(doctype, name, attachments):
	if isinstance(attachments, str):
		attachments = json.loads(attachments)
	files = []
	for a in attachments:
		if isinstance(a, str):
			attach = frappe.db.get_value("File", {"name": a}, ["file_name", "file_url", "is_private"], as_dict=1)
			f = save_url(attach.file_url, attach.file_name, doctype, name, "Home/Attachments", attach.is_private)
			files.append(f)
	return files

@frappe.whitelist()
def download_pdf(doctype, name, format=None, doc=None):
	html = frappe.get_print(doctype, name, format, doc=doc)
	frappe.local.response.filename = f"{name.replace(' ', '-').replace('/', '-')}.pdf"
	frappe.local.response.filecontent = get_pdf(html)
	frappe.local.response.type = "download"





########## Download Compliance Sheet ###########


def get_report_data(month,year,branch,company):
	custom_report = frappe.get_doc("Report", "Employee Salary Register")
	columns1, data = custom_report.run_query_report(filters={"month": month, "year": year, "branch": branch, "company": company}, user=frappe.session.user, ignore_prepared_report=True)
	return columns1, data


@frappe.whitelist()
def get_data(branch,state,company,for_month,pf_receipt,cd_doc_name):
	template = frappe.db.get_value("Compliance Requirement", {'state':state},"excel_template")
	if not template:
		frappe.throw(f'No template found for state :{state}. Please add template in Compliance Requirement')

	dt = datetime.strptime(for_month, "%b-%Y")
	month = dt.strftime("%b")
	year = dt.strftime("%Y")
	formatted_date = dt.strftime("%B %Y")
	year1 = int(year)
	month_no = list(calendar.month_abbr).index(month)
	
	filename = get_file_path(template)
	basename = filename.split("/")[-1]
	compliance_template_name = basename.split(".")[0]

	wb = load_workbook(filename)
	ws1= wb.get_sheet_by_name("employee_data")
	ws2= wb.get_sheet_by_name("attendance_data")
	ws3= wb.get_sheet_by_name("salary_data")
	ws4= wb.get_sheet_by_name("work_details")
	# ws5 = wb.get_sheet_by_name("")

	getlist_addrs = frappe.get_list("Address",fields = ["name"])
	esic_code,customer_name = frappe.db.get_value("Branch", {'name':branch}, ["esic_code", "customer"])

	parsed_date = datetime.strptime(for_month, "%b-%Y")
	first_day_of_next_month = parsed_date.replace(day=1) + timedelta(days=32 - parsed_date.day)
	sixth_day_of_next_month = first_day_of_next_month.replace(day=6)
	salary_date = sixth_day_of_next_month.strftime("%d-%m-%Y")

	sal_month = datetime.strptime(for_month, "%b-%Y")
	first_day_of_next_month = sal_month.replace(day=1) + timedelta(days=32 - parsed_date.day)
	salary_month = first_day_of_next_month.strftime("%b-%Y")

	ws4['C3'] = branch
	ws4['C4'] = state
	ws4['C10'] = esic_code
	ws4['C16'] = for_month
	ws4['C17'] = salary_date
	ws4['C18'] = salary_month

	
	for i in getlist_addrs:
		address_doc = frappe.get_doc("Address",i.name)
		for j in address_doc.links:
			if j.link_name == branch:
				ws4['C6'] = address_doc.address_line1
				ws4['C7'] = address_doc.address_line2
				ws4['C8'] = address_doc.address_line2
				ws4['C11'] = customer_name
			if j.link_name == company:
				ws4['C5'] = f'{address_doc.address_line1},{address_doc.address_line2}, {address_doc.state}, {address_doc.country}, {address_doc.state}, {address_doc.pincode}'
			if j.link_name == customer_name:
				ws4['C7'] = f'{address_doc.address_line1},{address_doc.address_line2},{address_doc.city}, {address_doc.pincode}'


	import tabula
	try:
		tables = tabula.read_pdf(get_file_path(pf_receipt), pages='1', multiple_tables=True)
		for table in tables:
			dt=table.to_csv()

			if dt.startswith(",TRRN No :,"):
				dt=dt.split(",TRRN No :,")[1]
				rows=dt.split("\n")
				ws4['C13'] = rows[0]

			if ",Total Amount (Rs) :," in dt:
				dt=dt.split(",Total Amount (Rs) :,")[1]
				rows=dt.split("\n")
				number_string = rows[0].replace('"', '').replace(',', '')
				ws4['C14'] = number_string

			if ",Payment Date :," in dt:
				dt=dt.split(",Payment Date :,")[1]
				rows=dt.split("\n")
				ws4['C15'] = rows[0]
	except Exception as e:
		frappe.msgprint(f"Error in PDF file if not attached please attach: {str(e)}")

	ws4['C13'],ws4['C14'],ws4['C15'] = frappe.db.get_value("Compliance Data", {'name':cd_doc_name}, ["trrn_number", "pf_receipt_amount","pf_receipt_date"])


	

	
	
	monthly_attndc_list = frappe.get_list("Monthly Attendance Upload", filters={"reference_doctype": company,"for_month": formatted_date})
	monthly_attndc_name = str(monthly_attndc_list[0]['name'])
	monthly_attndc_doc= frappe.get_doc("Monthly Attendance Upload", monthly_attndc_name)

	# columns1, data = get_report_data(month,year,branch,company)

	# as per saloni-Hr this commented 
	
	if branch == "Charanka_GIPCL":
		sub_branches = ["GIPCL_Plot 1","GIPCL_Plot 3"]
		columns1 = []
		data = []
		for branch in sub_branches:
			columns_lst, data_lsts = get_report_data(month,year,branch,company)

			# data.append(data_lsts)

			# data +=data_lsts
			data.extend(data_lsts)
			columns1=columns_lst
			# frappe.msgprint(f"Data for branch {branch}: {len(data)} records found.")
			# frappe.msgprint(f"columns1 : {columns1}")

		# frappe.msgprint(f"data :{data}")
	else:
		columns1, data = get_report_data(month,year,branch,company)

	data2 = []
	for i in data[:-1]:
		if isinstance(i, dict):
			if not i['employee'].startswith('C-PS'):
				data2.append(i)

	attendance_list = []
	for i in monthly_attndc_doc.attendance_details:
		for j in data[:-1]:
			if isinstance(j, dict):
				if j['employee'] == i.employee_id:
					attendance_array = i.attendance.split(',')
					attendance_list.append(attendance_array)

	for row_index, row_data in enumerate(attendance_list, start=3):
		for col_index, cell_value in enumerate(row_data, start=8):
			ws2.cell(row=row_index, column=col_index, value=cell_value)

	for index, value in enumerate(columns1):
		cell = ws3.cell(row=2, column=index + 1)
		cell.value = value.fieldname

	start_row = 3
	start_col = 1
	for row_num, dict_obj in enumerate(data2, start=start_row):
		for col_num, value in enumerate(dict_obj.values(), start=start_col):
			cell = ws3.cell(row=row_num, column=col_num)
			cell.value = value

	cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
	month_cal = cal.monthdatescalendar(year1, month_no)
	dates = [dt for week in month_cal for dt in week if dt.month == month_no]
	dates_str = [dt.strftime("%d/%b") for dt in dates]

	for rw in ws2['H2:AL2']:
		for cell, d in zip(rw, dates_str):
			cell.value = d

	count = 1
	thin = Side(border_style="thin", color="000000")

	start_row = 3
	atd_row = 3
	
	
	for d in data[:-1]:
		if isinstance(d, dict):
			doc = frappe.get_doc("Employee", d['employee'])
			if doc.employment_type != "Professional":
				# frappe.msgprint(str(doc.employee))
				ws1.cell(row=start_row, column=1).value = count
				ws1.cell(row=start_row, column=2).value = doc.employee
				ws1.cell(row=start_row, column=3).value = doc.employee_name
				ws1.cell(row=start_row, column=4).value = doc.branch
				ws1.cell(row=start_row, column=5).value = doc.first_name
				ws1.cell(row=start_row, column=6).value = doc.last_name
				ws1.cell(row=start_row, column=7).value = doc.middle_name
				# ws1.cell(row=start_row, column=8).value = doc.na
				ws1.cell(row=start_row, column=9).value = doc.gender
				ws1.cell(row=start_row, column=10).value = doc.date_of_birth
				ws1.cell(row=start_row, column=11).value = "India"
				ws1.cell(row=start_row, column=12).value = doc.esic_category
				# ws1.cell(row=start_row, column=11).value = doc.designation
				# ws1.cell(row=start_row, column=12).value = doc.uan
				# ws1.cell(row=start_row, column=13).value = doc.esic_number			
				ws1.cell(row=start_row, column=16).value = doc.date_of_joining
				ws1.cell(row=start_row, column=17).value = doc.cell_number
				ws1.cell(row=start_row, column=18).value = doc.pan_number
				ws1.cell(row=start_row, column=19).value = doc.adhaar_no
				ws1.cell(row=start_row, column=20).value = doc.bank_ac_no
				ws1.cell(row=start_row, column=21).value = doc.bank_name
				ws1.cell(row=start_row, column=22).value = doc.ifsc_code
				ws1.cell(row=start_row, column=23).value = doc.current_address
				ws1.cell(row=start_row, column=24).value = doc.permanent_address
				
				ws2.cell(row=atd_row, column=1).value = count
				ws2.cell(row=atd_row, column=2).value = doc.employee
				ws2.cell(row=atd_row, column=3).value = doc.employee_name
				ws2.cell(row=atd_row, column=4).value = doc.date_of_joining

				count = count+1
				start_row = start_row + 1
				atd_row = atd_row + 1

	for row in range(3, ws2.max_row + 1):
		ws2.cell(row=row, column=39).value = '=COUNTIF(H{}:AL{}, "P")'.format(row, row)
		ws2.cell(row=row, column=40).value = '=COUNTIF(H{}:AL{}, "LWP")'.format(row, row)
		ws2.cell(row=row, column=41).value = '=COUNTIF(H{}:AL{}, "WO")'.format(row, row)
		ws2.cell(row=row, column=42).value = '=COUNTIF(H{}:AL{}, "PH")'.format(row, row)
		ws2.cell(row=row, column=43).value = '=COUNTIF(H{}:AL{}, "PL") + COUNTIF(H{}:AL{}, "CL") + COUNTIF(H{}:AL{}, "SL") + COUNTIF(H{}:AL{}, "CO") + COUNTIF(H{}:AL{}, "CG")'.format(row, row, row, row, row, row,row, row, row, row)

	
	for row in ws1['A3':'AV' + str(ws1.max_row)]:
		for cell in row:
			cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

	for row in ws2['A3':'AR' + str(ws2.max_row)]:
		for cell in row:
			cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

	for row in ws3['A2':'AM' + str(ws3.max_row)]:
		for cell in row:
			cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

	filename_format = str(compliance_template_name+"-"+for_month)
	xlsx_file = BytesIO()
	wb.save(xlsx_file)
	frappe.response['filename'] = filename_format +'.xlsx'
	frappe.response['filecontent'] = xlsx_file.getvalue()
	frappe.response['type'] = 'binary'


# original

'''@frappe.whitelist()
def get_data(branch,state,company,for_month,pf_receipt,cd_doc_name):
	template_file_list = frappe.db.get_list("Compliance Requirement", filters={"state": state}, fields=["excel_template","state"],order_by=" effective_from desc",page_length=1)
	state,template = frappe.db.get_value("Compliance Requirement", {'state':state}, ["excel_template", "state"])
	frappe.msgprint(str(state))
	frappe.msgprint(str(template))
	if state ==template_file_list[0].state:
		if for_month == 'Sept-2025':
			for_month ='Sep-2025'
		dt = datetime.strptime(for_month, "%b-%Y")
		month = dt.strftime("%b")
		year = dt.strftime("%Y")
		formatted_date = dt.strftime("%B %Y")
		year1 = int(year)
		month_no = list(calendar.month_abbr).index(month)

		template_file=None
		template_file = template_file_list[0].excel_template
	
		if len(template_file) != 0:
			
			filename = get_file_path(template_file)
			basename = filename.split("/")[-1]
			compliance_template_name = basename.split(".")[0]

			wb = load_workbook(filename)
			ws1= wb.get_sheet_by_name("employee_data")
			ws2= wb.get_sheet_by_name("attendance_data")
			ws3 = wb.get_sheet_by_name("salary_data")
			ws4 = wb.get_sheet_by_name("work_details")
			# ws5 = wb.get_sheet_by_name("")

			getlist_addrs = frappe.get_list("Address",fields = ["name"])
			esic_code,customer_name = frappe.db.get_value("Branch", {'name':branch}, ["esic_code", "customer"])

			parsed_date = datetime.strptime(for_month, "%b-%Y")
			first_day_of_next_month = parsed_date.replace(day=1) + timedelta(days=32 - parsed_date.day)
			sixth_day_of_next_month = first_day_of_next_month.replace(day=6)
			salary_date = sixth_day_of_next_month.strftime("%d-%m-%Y")

			sal_month = datetime.strptime(for_month, "%b-%Y")
			first_day_of_next_month = sal_month.replace(day=1) + timedelta(days=32 - parsed_date.day)
			salary_month = first_day_of_next_month.strftime("%b-%Y")

			ws4['C3'] = branch
			ws4['C4'] = state
			ws4['C10'] = esic_code
			ws4['C16'] = for_month
			ws4['C17'] = salary_date
			ws4['C18'] = salary_month

			
			for i in getlist_addrs:
				address_doc = frappe.get_doc("Address",i.name)
				for j in address_doc.links:
					if j.link_name == branch:
						ws4['C6'] = address_doc.address_line1
						ws4['C7'] = address_doc.address_line2
						ws4['C8'] = address_doc.address_line2
						ws4['C11'] = customer_name
					if j.link_name == company:
						ws4['C5'] = f'{address_doc.address_line1},{address_doc.address_line2}, {address_doc.state}, {address_doc.country}, {address_doc.state}, {address_doc.pincode}'
					if j.link_name == customer_name:
						ws4['C7'] = f'{address_doc.address_line1},{address_doc.address_line2},{address_doc.city}, {address_doc.pincode}'


			import tabula
			try:
				tables = tabula.read_pdf(get_file_path(pf_receipt), pages='1', multiple_tables=True)
				for table in tables:
					dt=table.to_csv()

					if dt.startswith(",TRRN No :,"):
						dt=dt.split(",TRRN No :,")[1]
						rows=dt.split("\n")
						ws4['C13'] = rows[0]

					if ",Total Amount (Rs) :," in dt:
						dt=dt.split(",Total Amount (Rs) :,")[1]
						rows=dt.split("\n")
						number_string = rows[0].replace('"', '').replace(',', '')
						ws4['C14'] = number_string

					if ",Payment Date :," in dt:
						dt=dt.split(",Payment Date :,")[1]
						rows=dt.split("\n")
						ws4['C15'] = rows[0]
			except Exception as e:
				frappe.msgprint(f"Error in PDF file if not attached please attach: {str(e)}")


			ws4['C13'],ws4['C14'],ws4['C15'] = frappe.db.get_value("Compliance Data", {'name':cd_doc_name}, ["trrn_number", "pf_receipt_amount","pf_receipt_date"])

			
			
			monthly_attndc_list = frappe.get_list("Monthly Attendance Upload", filters={"reference_doctype": company,"for_month": formatted_date})
			monthly_attndc_name = str(monthly_attndc_list[0]['name'])
			monthly_attndc_doc= frappe.get_doc("Monthly Attendance Upload", monthly_attndc_name)
			
			custom_report = frappe.get_doc("Report", "Employee Salary Register")
			columns1, data = custom_report.run_query_report(filters={"month": month, "year": year, "branch": branch, "company": company}, user=frappe.session.user, ignore_prepared_report=True)
			# if len(data) == 0:
			# 	frappe.throw('Data Is Not Available')
			# elif len(data) == 1:
			# 	frappe.msgprint(str(data))
			# else:
			# 	data.pop()
			# 	frappe.msgprint(str(data))
			# 	# # data = json.loads(data)
			# 	for i in data[0]:
			# 		frappe.msgprint(str(i['employee']))

			# return


			data2 = []
			for i in data[:-1]:
				if not i['employee'].startswith('C-PS'):
					data2.append(i)

			attendance_list = []
			for i in monthly_attndc_doc.attendance_details:
				for j in data[:-1]:
					if j['employee'] == i.employee_id:
						attendance_array = i.attendance.split(',')
						attendance_list.append(attendance_array)

			for row_index, row_data in enumerate(attendance_list, start=3):
				for col_index, cell_value in enumerate(row_data, start=8):
					ws2.cell(row=row_index, column=col_index, value=cell_value)

			for index, value in enumerate(columns1):
				cell = ws3.cell(row=2, column=index + 1)
				cell.value = value.fieldname

			start_row = 3
			start_col = 1
			for row_num, dict_obj in enumerate(data2, start=start_row):
				for col_num, value in enumerate(dict_obj.values(), start=start_col):
					cell = ws3.cell(row=row_num, column=col_num)
					cell.value = value

			cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
			month_cal = cal.monthdatescalendar(year1, month_no)
			dates = [dt for week in month_cal for dt in week if dt.month == month_no]
			dates_str = [dt.strftime("%d/%b") for dt in dates]

			for rw in ws2['H2:AL2']:
				for cell, d in zip(rw, dates_str):
					cell.value = d

			count = 1
			thin = Side(border_style="thin", color="000000")

			start_row = 3
			atd_row = 3
			
			for d in data[:-1]:
				doc = frappe.get_doc("Employee", d['employee'])
				if doc.employment_type == "Professional":
					pass
				else:
					# frappe.msgprint(str(doc.employee))
					ws1.cell(row=start_row, column=1).value = count
					ws1.cell(row=start_row, column=2).value = doc.employee
					ws1.cell(row=start_row, column=3).value = doc.employee_name
					ws1.cell(row=start_row, column=4).value = doc.branch
					ws1.cell(row=start_row, column=5).value = doc.first_name
					ws1.cell(row=start_row, column=6).value = doc.last_name
					ws1.cell(row=start_row, column=7).value = doc.middle_name
					# ws1.cell(row=start_row, column=8).value = doc.na
					ws1.cell(row=start_row, column=9).value = doc.gender
					ws1.cell(row=start_row, column=10).value = doc.date_of_birth
					ws1.cell(row=start_row, column=11).value = "India"
					ws1.cell(row=start_row, column=12).value = doc.esic_category
					# ws1.cell(row=start_row, column=11).value = doc.designation
					# ws1.cell(row=start_row, column=12).value = doc.uan
					# ws1.cell(row=start_row, column=13).value = doc.esic_number			
					ws1.cell(row=start_row, column=16).value = doc.date_of_joining
					ws1.cell(row=start_row, column=17).value = doc.cell_number
					ws1.cell(row=start_row, column=18).value = doc.pan_number
					ws1.cell(row=start_row, column=19).value = doc.adhaar_no
					ws1.cell(row=start_row, column=20).value = doc.bank_ac_no
					ws1.cell(row=start_row, column=21).value = doc.bank_name
					ws1.cell(row=start_row, column=22).value = doc.ifsc_code
					ws1.cell(row=start_row, column=23).value = doc.current_address
					ws1.cell(row=start_row, column=24).value = doc.permanent_address
					
					ws2.cell(row=atd_row, column=1).value = count
					ws2.cell(row=atd_row, column=2).value = doc.employee
					ws2.cell(row=atd_row, column=3).value = doc.employee_name
					ws2.cell(row=atd_row, column=4).value = doc.date_of_joining

					count = count+1
					start_row = start_row + 1
					atd_row = atd_row + 1

			for row in range(3, ws2.max_row + 1):
				ws2.cell(row=row, column=39).value = '=COUNTIF(H{}:AL{}, "P")'.format(row, row)
				ws2.cell(row=row, column=40).value = '=COUNTIF(H{}:AL{}, "LWP")'.format(row, row)
				ws2.cell(row=row, column=41).value = '=COUNTIF(H{}:AL{}, "WO")'.format(row, row)
				ws2.cell(row=row, column=42).value = '=COUNTIF(H{}:AL{}, "PH")'.format(row, row)
				ws2.cell(row=row, column=43).value = '=COUNTIF(H{}:AL{}, "PL") + COUNTIF(H{}:AL{}, "CL") + COUNTIF(H{}:AL{}, "SL") + COUNTIF(H{}:AL{}, "CO") + COUNTIF(H{}:AL{}, "CG")'.format(row, row, row, row, row, row,row, row, row, row)
	
			
			for row in ws1['A3':'AV' + str(ws1.max_row)]:
				for cell in row:
					cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

			for row in ws2['A3':'AR' + str(ws2.max_row)]:
				for cell in row:
					cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

			for row in ws3['A2':'AM' + str(ws3.max_row)]:
				for cell in row:
					cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

			# filename_format = str(compliance_template_name+"-"+for_month)
			# xlsx_file = BytesIO()
			# wb.save(xlsx_file)
			# frappe.response['filename'] = filename_format +'.xlsx'
			# frappe.response['filecontent'] = xlsx_file.getvalue()
			# frappe.response['type'] = 'binary'
		else:
			frappe.throw(f"Template file not found in Compliance Requirement for {state}")
'''



@frappe.whitelist()
def generate_esic_xls(sp_doc_name):
	sheet = []
	doc = frappe.get_doc("Compliance Data", sp_doc_name).as_dict()

	dict1= ["IP Number (10 Digits)","IP Name( Only alphabets and space )","No of Days for which wages paid/payable during the month","Total Monthly Wages","Reason Code for Zero workings days(numeric only; provide 0 for all other reasons- Click on the link for reference)","Last Working Day( Format DD/MM/YYYY  or DD-MM-YYYY)"]

	# column_list = list(doc2[0].keys())
	# column_list = list(dict1.keys())
	sheet.append(dict1)
	date_string = doc.month_year
	date_parts = date_string.split('-')
	month = date_parts[0]
	year = date_parts[1]
	final_month = month[:3]
	report_data = frappe.get_doc('Report', 'Employee Salary Register')
	columns, result = report_data.run_query_report(filters={'month':final_month,'year':year,'company':doc.company,'branch':doc.branch} ,user=frappe.session.user)
	#frappe.throw(json.dumps(result, indent=4, sort_keys=True, default=str))
	sal_reg_dict=dict()
	if result:
		for r in result[:-1]:
			if r["esic[deductions]"]>0.0:
				employee_bank_name,employee_name,esic_number,relieving_date=frappe.db.get_value("Employee",r["employee"],["name_as_per_bank","employee_name","esic_number","relieving_date"])
				if relieving_date is None:relieving_date=""
				esic_row=[esic_number,employee_name,r["pay_days"], round(r["esic[deductions]"]*133.333),"",relieving_date]
				sheet.append(esic_row)
		from frappe_addons.fileutils import list_to_xls_response
		list_to_xls_response(sheet,"sheet1",sp_doc_name + '_esic_'+doc.branch+'.xls')
	else:
		frappe.msgprint("Data not loaded yet")


	'''
	myfile = BytesIO()
	myfile.write(save_virtual_workbook(wb))
	frappe.response["filecontent"] = myfile.getvalue()
	frappe.response["filename"] =  sp_doc_name + '_esic_'+doc.branch+'.xls'
	frappe.response["content_type"]='application/vnd.openxmlformats-officedocameent.spreadsheetml.sheet'
	#frappe.response["mimetype"] =  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
	frappe.response["type"] = "binary"
	'''


'''@frappe.whitelist()
def download_multi_pdf(doctype, docname, state):
	output = PdfWriter()
	comp_req_doc_list = frappe.db.get_list('Compliance Requirement', filters={'state': state})
	comp_req_doc = frappe.get_doc("Compliance Requirement", comp_req_doc_list[0]["name"])
	count = 0
	html = None
	for report in comp_req_doc.print_formats:
		if report.report_type == "Print Format":
			options = { 'orientation': report.orientation }
			try:
				html = frappe.get_print(doctype, docname, report.print_format, as_pdf=True, output=output, pdf_options=options)
			except Exception:
				frappe.log_error("Error in Multi PDF download", f"Permission Error on doc {doctype} of doctype {docname}")
		if report.report_type == "PDF":
			# frappe.msgprint(list(report.fieldname))
			field = report.fieldname
			pdf_file_path = frappe.db.get_value(doctype, docname, field)
			if pdf_file_path:
				pdf_reader = PdfReader(get_file_path(pdf_file_path))
				
				if report.pages is None:
					for page in pdf_reader.pages:
						# output.add_page(page)
						frappe.msgprint(str(page))
				else:
					if "," in report.pages:
						selected_pages = report.pages.split(',')
						for pagenum in selected_pages:
							output.add_page(pdf_reader.pages[int(pagenum)-1])
					else:
						output.add_page(pdf_reader.pages[int(report.pages)-1])
		count += 1
		frappe.publish_progress(count * 100 / len(comp_req_doc.print_formats), title=_("PDF Generating!!"))
	if html:
		frappe.local.response.filename = f"{docname.replace(' ', '-').replace('/', '-')}.pdf"
		frappe.local.response.filecontent = read_multi_pdf(html)
		frappe.local.response.type = "download"'''


# after format changed need to remove some content

@frappe.whitelist()
def download_multi_pdf(doctype, docname, state):
	output = PdfWriter()
	comp_req_doc_list = frappe.db.get_list('Compliance Requirement', filters={'state': state})
	comp_req_doc = frappe.get_doc("Compliance Requirement", comp_req_doc_list[0]["name"])
	count = 0
	html = None
	for report in comp_req_doc.print_formats:
		if report.report_type == "Print Format":
			options = {'orientation': report.orientation}
			frappe.msgprint(str(report.print_format))
			
			try:
				html = frappe.get_print(doctype, docname, report.print_format, as_pdf=True, output=output, pdf_options=options)
			except Exception:
				frappe.log_error("Error in Multi PDF download", f"Permission Error on doc {doctype} of doctype {docname}")
		if report.report_type == "PDF":
			field = report.fieldname
			pdf_file_path = frappe.db.get_value(doctype, docname, field)
			if pdf_file_path:
				pdf_reader = PdfReader(get_file_path(pdf_file_path))

				if report.fieldname == "pf_ecr":
					# Clean the first page (mask out table)
					cleaned_page = remove_member_details_section(get_file_path(pdf_file_path))
					output.add_page(cleaned_page)
				elif report.pages is None:
					for page in pdf_reader.pages:
						output.add_page(page)
				else:
					if "," in report.pages:
						selected_pages = report.pages.split(',')
						for pagenum in selected_pages:
							output.add_page(pdf_reader.pages[int(pagenum)-1])
					else:
						output.add_page(pdf_reader.pages[int(report.pages)-1])
		count += 1
		frappe.publish_progress(count * 100 / len(comp_req_doc.print_formats), title=_("PDF Generating!!"))
	if html:
		frappe.local.response.filename = f"{docname.replace(' ', '-').replace('/', '-')}.pdf"
		frappe.local.response.filecontent = read_multi_pdf(html)
		frappe.local.response.type = "download"


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO

def remove_member_details_section(pdf_path):
    '''
    This is for pf_ecr field in doctype compliance data.
    Need to remove some content from a page.
    '''
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    
    # Get the actual page dimensions
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
    
    # Create an overlay (white rectangle)
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
    
    # Set white fill color
    can.setFillColorRGB(1, 1, 1)
    
    # Cover the member details table section
    # Based on your EPF document, the table starts around row 11
    # Adjust y_start to position where the table begins
    # The table appears to be in the lower portion of the page
    
    # Option 1: Cover entire bottom section (from bottom to a certain height)
    y_start = 0  # Bottom of page
    y_end = 350  # Adjust this value to cover the table height
    can.rect(285, y_start, page_width, 850, fill=True, stroke=False)
    
    # Option 2: If you want to keep some bottom content and only hide middle section
    # Uncomment below and adjust coordinates:
    # y_start = 200  # Distance from bottom
    # y_end = 600    # Distance from bottom
    # height = y_end - y_start
    # can.rect(0, y_start, page_width, height, fill=True, stroke=False)
    
    can.save()
    
    # Merge overlay
    packet.seek(0)
    overlay_pdf = PdfReader(packet)
    page.merge_page(overlay_pdf.pages[0])
    
    return page


# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# def remove_member_details_section(pdf_path):

# 	'''
# 		This is for pf_ecr field in doctype complience data.
# 		Need to remove some content from a page.
# 	'''
# 	reader = PdfReader(pdf_path)
# 	page = reader.pages[0]
	
# 	# Create an overlay (white rectangle)
# 	packet = BytesIO()
# 	can = canvas.Canvas(packet, pagesize=letter)

# 	page_width, page_height = "A4"  # (595, 842)

    
#     # Adjust these coordinates based on where your table starts on the page
#     # (x=left margin, y=bottom margin)
#     # You can tweak this to cover the whole lower half of the page if unsure
# 	can.setFillColorRGB(1, 1, 1)  # white
# 	# can.rect(0, 0, 200, 900, fill=True, stroke=False)  # cover bottom half
# 	# can.rect(300, 0, 595, 842, fill=True, stroke=False) this one close 
# 	can.rect(285, 0, 585, 842, fill=True, stroke=False) #this one now covering Member Details :- as well  

# 	# can.rect(285, 0, 400, 942, fill=True, stroke=False)
# 	# can.rect(0, 400, 400, 942, fill=True, stroke=False)

# 	can.save()

# 	# Merge overlay
# 	packet.seek(0)
# 	overlay_pdf = PdfReader(packet)
# 	page.merge_page(overlay_pdf.pages[0])

# 	return page






@frappe.whitelist()
def get_attach_fields():
	return frappe.get_all("DocField", {"parent": "Compliance Data", "fieldtype": "Attach"}, ["fieldname"])








'''
@frappe.whitelist()
	def extract_pdf_data(self):
		date_string = self.month_year
		date_parts = date_string.split('-')
		month = date_parts[0]
		year = date_parts[1]
		final_month = month[:3]
		report_data = frappe.get_doc('Report', 'Employee Salary Register')
		uan_list = []
		columns, result = report_data.run_query_report(filters={'month': final_month, 'year': year, 'branch': self.branch, 'company': self.company}, user=frappe.session.user)

		for report_data in result[:-1]:
			uan_list.append(report_data["uan"])
		parts = []
		attach_list = get_attachments(self.doctype, self.name)
		import tabula
		tables = tabula.read_pdf(get_file_path(self.pf_ecr), pages='all', multiple_tables=True)
		frappe.msgprint(str(tables))
		data_dict = {}
		for table in tables:
			dt = table.to_csv()
			frappe.msgprint(str(dt))
			if dt.startswith(",Sl. No.,") and "EE Share,," in dt:
				dt = dt.split("EE Share,,")[1]
				rows = dt.split("\n")
				for row in rows:
					cols = row.split(",")
					if cols and any(cols):
						if cols[2].endswith(".0"):
							cols[2] = cols[2][:-2]
					if row.strip().endswith("N.A."):
						row = re.sub(r'(?!(([^\"]*\"){2})*[^\"]*$),', '', row)
						data_dict[cols[2]] = row.replace('"', '').split(",")

		

		return
		selected_rows = []
		for key in data_dict:
			d = {
				"uan": key,
				"gross": data_dict[key][5],
				"epf": data_dict[key][6],
				"eps": data_dict[key][7],
				"edli": data_dict[key][8],
				"refunds": data_dict[key][13],
				"is_abry": 0,
				"ee_cr": data_dict[key][9],
				"eps_cr": data_dict[key][10],
				"er_cr": data_dict[key][11],
				"ncp_days_cr": data_dict[key][12]
			}
			if data_dict[key][14] == "ABRY":
				d["is_abry"] = 1
			if key in uan_list:
				selected_rows.append(d)
		return selected_rows'''