import asyncio
from src.db.session import get_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.models.algorithms import Algorithm, Curve
from src.db.models.users import User, Role

async def main():
    async with AsyncSession(get_engine()) as session:
        # Query algorithms
        algorithms = await session.execute(select(Algorithm))
        algo_result = algorithms.scalars().all()
        print(f'Found {len(algo_result)} algorithms:')
        for algo in algo_result:
            print(f'- {algo.name} ({algo.type}): {algo.description}')
        
        # Query curves
        curves = await session.execute(select(Curve))
        curve_result = curves.scalars().all()
        print(f'\nFound {len(curve_result)} curves:')
        for curve in curve_result:
            print(f'- {curve.name}: {curve.description}')
        
        # Query roles
        roles = await session.execute(select(Role))
        role_result = roles.scalars().all()
        print(f'\nFound {len(role_result)} roles:')
        for role in role_result:
            print(f'- {role.name}: {role.description}')
        
        # Query users
        users = await session.execute(select(User))
        user_result = users.scalars().all()
        print(f'\nFound {len(user_result)} users:')
        for user in user_result:
            print(f'- {user.username} ({user.email}): {user.full_name}')

asyncio.run(main()) 