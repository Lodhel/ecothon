from sqlalchemy import select


async def get_or_create(session, model, **kwargs):
    instance_by_select = await session.execute(select(model).filter_by(**kwargs))
    if instance := instance_by_select.scalars().first():
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        await session.flush()
        return instance
