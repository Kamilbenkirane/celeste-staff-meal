<div align="center">

# Celeste Staff Meal

**UberEats / Deliveroo Order Verification Platform**

Verify every order before closing the bag to prevent preparation errors.

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-red?style=for-the-badge)](LICENSE)

[Installation](#-installation) • [Usage](#-usage) • [Features](#-features)

</div>

---

## 🎯 Objective

Prevent preparation errors by verifying every order before closing the bag. Zero missing items, fewer complaints, better ratings on delivery platforms.

---

## 🚀 Installation

```bash
git clone <repository-url>
cd celeste-staff-meal
make sync
```

---

## 💡 Usage

```python
from staff_meal import verify_order

result = await verify_order(
    ticket_image="path/to/ticket.jpg",
    bag_image="path/to/bag.jpg"
)

if result.is_complete:
    print("✅ Order complete — you can close the bag")
else:
    print(f"❌ Missing items: {', '.join(result.missing_items)}")
```

**Input:** Ticket photo + bag contents photo
**Output:** Validation with list of missing products if necessary

---

## 📋 Features

- **Order reading**: OCR from ticket or UberEats/Deliveroo integration
- **Visual analysis**: Detection of items in the bag (boxes, drinks, sauces)
- **Validation**: Clear "Missing / OK" screen with list of missing items
- **Statistics**: Complete order rate, frequently forgotten products

---

## 🎁 Benefits

- Reduction in "missing product" complaints
- Better ratings on UberEats / Deliveroo
- Less stress at dispatch
- Complete traceability

---

## ⚙️ Constraints

- Verification in less than 5 seconds
- Interface usable with dirty hands (large buttons, minimal text)
- Compatible with simple smartphone/tablet
- No complicated configuration

---

## 🧪 Development

```bash
make test      # Run tests
make lint      # Run linting
make typecheck # Run type checking
make ci        # Run full CI pipeline
```

---

## 📄 License

Apache 2.0 license – see [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ for restaurants

</div>
