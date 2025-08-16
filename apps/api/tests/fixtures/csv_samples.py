"""
CSV sample data for testing purposes.
"""

# Basic CSV sample with mixed valid and invalid data
BASIC_CSV_SAMPLE = """sku,title,price,stock,category
SKU001,Product 1,10.99,5,Electronics
SKU002,Product 2,25.50,0,Clothing
,Product 3,-5,10,Electronics
SKU004,,30.00,-1,"""

# Valid CSV sample
VALID_CSV_SAMPLE = """sku,title,price,stock,category
SKU001,Product 1,10.99,5,Electronics
SKU002,Product 2,25.50,10,Clothing
SKU003,Product 3,15.00,0,Electronics
SKU004,Product 4,30.00,20,Home"""

# Invalid CSV sample with multiple errors
INVALID_CSV_SAMPLE = """sku,title,price,stock,category
,,-5,-10,
SKU002,,,invalid_stock,
SKU003,Product 3,not_a_price,10,Electronics
,,,,"""

# Large CSV sample for performance testing
def generate_large_csv_sample(rows: int = 1000) -> str:
    """Generate a large CSV sample for performance testing."""
    header = "sku,title,price,stock,category"
    lines = [header]
    
    for i in range(rows):
        sku = f"SKU{i:05d}"
        title = f"Product {i}"
        price = f"{10.0 + (i % 100):.2f}"
        stock = i % 50
        category = ["Electronics", "Clothing", "Home", "Sports"][i % 4]
        lines.append(f"{sku},{title},{price},{stock},{category}")
    
    return "\n".join(lines)

# Marketplace-specific samples
MERCADO_LIVRE_SAMPLE = """sku,title,price,stock,category,brand,condition
MLB001,Notebook Dell Inspiron,2500.00,10,Informática,Dell,new
MLB002,Tênis Nike Air Max,350.50,5,Esportes,Nike,new
MLB003,Cafeteira Expresso,150.00,0,Eletrodomésticos,Nespresso,used"""

AMAZON_SAMPLE = """sku,title,price,stock,category,asin,fulfillment
AMZ001,Echo Dot (4th Gen),49.99,100,Smart Home,B07XJ8C8F5,FBA
AMZ002,Fire TV Stick 4K,39.99,50,Electronics,B08XVYZ1Y5,FBA
AMZ003,Kindle Paperwhite,129.99,25,E-readers,B08KTZ8249,FBM"""