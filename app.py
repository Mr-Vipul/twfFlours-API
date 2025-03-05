from flask import Flask, request, jsonify
from itertools import permutations

app = Flask(__name__)

# Define the stock details for each center
centers = {
    "C1": {"A": 3, "B": 2, "C": 8},
    "C2": {"D": 12, "E": 25, "F": 15},
    "C3": {"G": 0.5, "H": 1, "I": 2}
}

# Define the distances from each center to L1
distances = {
    "C1": 3,
    "C2": 4,
    "C3": 2
}

# Define the cost per unit distance based on weight
def calculate_cost(weight, distance):
    if weight <= 5:
        return 10 * distance
    else:
        additional_weight = weight - 5
        additional_cost = (additional_weight // 5) * 8 * distance
        if additional_weight % 5 != 0:
            additional_cost += 8 * distance
        return 10 * distance + additional_cost

# Function to calculate the minimum cost for a given order
def calculate_minimum_cost(order):
    min_cost = float('inf')
    
    # Get the list of centers that have products in the order
    active_centers = []
    for center, products in centers.items():
        for product in products:
            if product in order and order[product] > 0:
                active_centers.append(center)
                break
    
    # Generate all possible routes (permutations of active centers)
    for route in permutations(active_centers):
        # Start at the first center in the route
        current_center = route[0]
        total_distance = distances[current_center]  # Distance from current center to L1
        total_weight = 0
        
        # Calculate the weight of products from the first center
        for product, quantity in order.items():
            if product in centers[current_center]:
                total_weight += centers[current_center][product] * quantity
        
        # Calculate the cost for the first segment (current center to L1)
        cost = calculate_cost(total_weight, distances[current_center])
        
        # Iterate through the remaining centers in the route
        for next_center in route[1:]:
            # Add distance from L1 to the next center
            total_distance += distances[next_center]
            
            # Calculate the weight of products from the next center
            next_weight = 0
            for product, quantity in order.items():
                if product in centers[next_center]:
                    next_weight += centers[next_center][product] * quantity
            
            # Add the weight of products from the next center
            total_weight += next_weight
            
            # Calculate the cost for the next segment (L1 to next center to L1)
            cost += calculate_cost(total_weight, distances[next_center])
        
        # Update the minimum cost
        if cost < min_cost:
            min_cost = cost
    
    return min_cost

# Define the API endpoint
@app.route('/calculate-cost', methods=['POST'])
def calculate_cost_api():
    try:
        # Get the JSON data from the request
        order = request.get_json()
        
        # Calculate the minimum cost
        min_cost = calculate_minimum_cost(order)
        
        # Return the result as JSON
        return jsonify({"minimum_cost": min_cost})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)