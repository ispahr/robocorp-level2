from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        # browser_engine="chrome",
        slowmo=100,
    )
    open_robot_order_website("https://robotsparebinindustries.com/#/")
    close_annoying_modal()
    orders = get_orders()
    fill_the_form(orders)
    # process_orders(orders)
    archive_receipts()

def open_robot_order_website(url: str):
    browser.goto(url)

def get_orders():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv",overwrite=True)
    library = Tables()
    orders_table = library.read_table_from_csv("orders.csv")
    
    return orders_table

def process_orders(orders_table):
    
    for order in orders_table:
        print(order)
        
def close_annoying_modal():
    page = browser.page()
    page.click(selector="a:text('Order your robot!')")
    page.click(selector="button:text('Ok')")
    
def fill_the_form(orders):
    page = browser.page()
    page.click("button:text('Show model info')")
    data = page.locator("#model-info").text_content()
    
    for order in orders:
        page = browser.page()
        page.select_option("#head",order["Head"])
        page.check("#id-body-"+str(order["Body"]))
        page.fill(".form-control",str(order["Legs"]))
        page.fill("#address",order["Address"])
        page.click("#order")
    
        page = browser.page()
        sucess_visible = page.locator(".badge.badge-success").is_visible()
        while sucess_visible==False:
            page.click("#order")
            sucess_visible = page.locator(".badge.badge-success").is_visible()
        
        order_number = page.locator(".badge.badge-success").text_content()
        pdf_path = store_receipt_as_pdf(str(order_number))
        screenshot_path = screenshot_robot(str(order_number))
        embed_screenshot_to_receipt(screenshot_path,pdf_path)
        
        page.click("#order-another")
        page.click(selector="button:text('Ok')")
        
        
def store_receipt_as_pdf(order_number : str)-> str:
    page = browser.page()
    html = page.locator("#receipt").inner_html()
    path = f"output/{order_number}-receipt.pdf"
    pdf = PDF()
    pdf.html_to_pdf(html, path)
    return path

def screenshot_robot(order_number: str)-> str:
    page = browser.page()
    path = f"output/{order_number}-screenshot.png"
    page.locator("#robot-preview-image").screenshot(path=path)
    return path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(
        files=[screenshot,],
        target_document=pdf_file,
        append=True
    )

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output', './output/robottasks.zip', include='*.pdf')
    