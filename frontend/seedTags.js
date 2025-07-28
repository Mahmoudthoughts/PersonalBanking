const axios = require('axios');

const BASE_URL = 'http://localhost:5000/tags';
const AUTH_TOKEN = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MzY5MzAwMCwianRpIjoiYmFjYTlmMDMtYWRhZi00NDRhLTg5M2MtNWQ5YmM5MGU0ZjgyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NTM2OTMwMDAsImNzcmYiOiIyMmZiOWQzZS05MmI3LTRiNzgtYTc5YS1kZDBhNWJmMzEyNGMiLCJleHAiOjE3NTM2OTM5MDB9.XSg55wnEIAtybGLeyOxa6-dyEAuOD23YWDSX6SuNlU4'; // Replace with your actual token

const headers = {
  'Authorization': AUTH_TOKEN,
  'Content-Type': 'application/json'
};

const tagTree = {
  "Income": ["Wages & Tips", "Interest Income", "Dividends", "Gifts Received", "Refunds/Reimbursements", "Transfer from Savings", "Other"],
  "Home Expenses": ["Mortgage/Rent", "Electricity", "Gas/Oil", "Water/Sewer/Trash", "Phone", "Cable/Satellite", "Internet", "Furnishings/Appliances", "Lawn/Garden", "Home Supplies", "Maintenance", "Improvements", "Other"],
  "Daily Living": ["Groceries", "Personal Supplies", "Clothing", "Cleaning Services", "Dining/Eating Out", "Dry Cleaning", "Salon/Barber", "Discretionary [Name 1]", "Discretionary [Name 2]", "Other"],
  "Children": ["Medical", "Clothing", "School Tuition", "School Lunch", "School Supplies", "Babysitting", "Toys/Games", "Other"],
  "Transportation": ["Vehicle Payments", "Fuel", "Bus/Taxi/Train Fare", "Repairs", "Registration/License", "Other"],
  "Health": ["Doctor/Dentist", "Medicine/Drugs", "Health Club Dues", "Emergency", "Other"],
  "Insurance": ["Auto", "Health", "Home/Rental", "Life", "Other"],
  "Education": ["Music Lessons", "Tuition", "Other"],
  "Charity/Gifts": ["Gifts Given", "Charitable Donations", "Religious Donations", "Other"],
  "Savings": ["Emergency Fund", "Car Replacement Fund", "Retirement Fund", "Investments", "Education Fund", "Other"],
  "Obligations": ["Student Loans", "Credit Card Debt", "Other Loans", "Alimony/Child Support", "Federal Taxes", "State/Local Taxes", "Legal Fees", "Other"],
  "Business Expense": ["Deductible Expenses", "Non-Deductible Expenses", "Other"],
  "Entertainment": ["Activities", "Books", "Games", "Fun Stuff", "Hobbies", "Media", "Outdoor Recreation", "Sports", "Toys/Gadgets", "Vacation/Travel", "Other"],
  "Pets": ["Food", "Medical", "Toys/Supplies", "Other"],
  "Subscriptions": ["Newspaper", "Magazines", "Dues", "Club Memberships", "Other"],
  "Vacation": ["Travel", "Lodging", "Food", "Rental Car", "Entertainment", "Other"],
  "Miscellaneous": ["Bank Fees", "Postage", "Other"]
};

async function seedTags() {
  const parentIds = {};

  for (const parent of Object.keys(tagTree)) {
    const parentRes = await axios.post(BASE_URL, {
      name: parent,
      parent_id: ""
    }, { headers });

    const parentId = parentRes.data.id;
    parentIds[parent] = parentId;

    console.log(`Created parent: ${parent} → ID: ${parentId}`);

    for (const child of tagTree[parent]) {
      const childRes = await axios.post(BASE_URL, {
        name: child,
        parent_id: parentId
      }, { headers });

      console.log(`  ↳ Created child: ${child} → ID: ${childRes.data.id}`);
    }
  }

  console.log('\n✅ All categories and subcategories created.');
}

seedTags().catch(err => {
  console.error('❌ Error:', err.response?.data || err.message);
});
