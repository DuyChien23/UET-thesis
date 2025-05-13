import asyncio
from src.algorithms import initialize_algorithms, load_algorithms_from_db
from src.core.registry import get_algorithm_registry

async def main():
    # Initialize algorithm providers
    providers = initialize_algorithms()
    print(f'Initialized {len(providers)} algorithm providers: {list(providers.keys())}')
    
    # Load algorithms from database
    db_data = await load_algorithms_from_db()
    
    # Set database data in registry
    registry = get_algorithm_registry()
    registry.set_db_data(db_data)
    
    # Check if database data is loaded
    print(f'\nLoaded {len(db_data)} algorithms from database:')
    for algo_name, algo_data in db_data.items():
        print(f'- {algo_name} ({algo_data["type"]}): {len(algo_data["curves"])} curves')
        for curve_name, curve_data in algo_data["curves"].items():
            print(f'  * {curve_name}: {curve_data["description"]}')

if __name__ == "__main__":
    asyncio.run(main()) 