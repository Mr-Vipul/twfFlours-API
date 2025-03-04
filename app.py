from flask import Flask, request, jsonify
from itertools import permutations

app = Flask(__name__)

# Product information and distances (assumed)
product_info = {
    'A': {'center': 'C1', 'weight': 3},
    'B': {'center': 'C1', 'weight': 2},
    'C': {'center': 'C1', 'weight': 8},
    'D': {'center': 'C2', 'weight': 12},
    'E': {'center': 'C2', 'weight': 25},
    'F': {'center': 'C2', 'weight': 15},
    'G': {'center': 'C3', 'weight': 0.5},
    'H': {'center': 'C3', 'weight': 1},
    'I': {'center': 'C3', 'weight': 2},
}

center_distances = {
    'C1': 3,  
    'C2': 4, 
    'C3': 2,
}

def calculate_cost_per_unit(total_weight):
    """Calculate cost per unit distance based on weight tiers"""
    if total_weight <= 5:
        return 10
    additional = (total_weight - 5) // 5 
    return 10 + (additional * 8)

def compute_min_cost(order):
    """Calculate minimum delivery cost for the given order"""
    centers_needed = set()
    center_weights = {'C1': 0, 'C2': 0, 'C3': 0}
    
    # Process order items
    for product, qty in order.items():
        if qty <= 0 or product not in product_info:
            continue
        info = product_info[product]
        center = info['center']
        centers_needed.add(center)
        center_weights[center] += info['weight'] * qty
    
    centers_needed = [c for c in centers_needed if center_weights[c] > 0]
    if not centers_needed:
        return 0 
    
    min_cost = float('inf')
    
    for start_center in ['C1', 'C2', 'C3']:
        other_centers = [c for c in centers_needed if c != start_center]
    
        for perm in permutations(other_centers):
            route = [start_center] + list(perm) + ['L1']
            total_weight = 0
            current_cost = 0
            previous_stop = start_center
            
            for next_stop in route[1:]:

                if previous_stop == 'L1':
                    break
                
                if next_stop == 'L1':
                    distance = center_distances[previous_stop]
                else:
                    distance = center_distances[previous_stop] + center_distances[next_stop]
                
                if previous_stop != 'L1':
                    total_weight += center_weights.get(previous_stop, 0)
                
                cost_per_unit = calculate_cost_per_unit(total_weight)
                leg_cost = distance * cost_per_unit
                current_cost += leg_cost
                previous_stop = next_stop
            
            if current_cost < min_cost:
                min_cost = current_cost
    
    return min_cost

@app.route('/calculate-cost', methods=['POST'])
def calculate_delivery_cost():
    try:
        order = request.get_json()
        if not order:
            return jsonify({"error": "Empty request"}), 400
        
        # Validate product names
        valid_products = product_info.keys()
        for product in order.keys():
            if product not in valid_products:
                return jsonify({"error": f"Invalid product {product}"}), 400
        
        min_cost = compute_min_cost(order)
        return jsonify({"minimum_cost": min_cost})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)