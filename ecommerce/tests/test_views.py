
# Test ProductListView
# Check for correct template
# Test Empty product db models displays "No Products Found" message
# Loads all products without any category
# Loads correct category on passing category as GET params
# Unknown category displays a "No Products Found" message
# Test if banner image is added to context
# Test if max 3 banner image is added to context

# Test get_total_price_of_cart
# with empty cart

# Test CardListView
# Check for correct template
# Check login required
# context['cart_list'] loads correct cart
# context['total'] shows the correct total

# Test CartAddView
# check get request returns home template
# check post request adds item to cart and redirects to cart
# check with unknown product, raises http404
# Check with already existing cart item
# check request without product, raises http404

# OrderListView
# Returns all orders of correct user
# Test template

# OrderDetailView
# Returns correct template
# Returns correct order with all the products

# CheckOut page View
# Test template
# test get cart list function
# get request
#   - check wallet balance
#   - check cart_list
#   - check total_price
#   - empty cart list redirects to cart
# place order form cart
#   - with empty cart list
#   - Negative total_amount, 0 total_amount
#   - Check if creates correct order with correct items
# post
#   - post with empty cart
#   - post with less wallet balance
#   - check template on success
#   - check order in context
