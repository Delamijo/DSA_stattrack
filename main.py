from nicegui import ui


@ui.page('/')
def heldenbogen():
    ui.label('DSA Heldenbogen').classes('text-2xl')
    ui.button('Test', on_click=lambda: ui.notify('funktioniert'))


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title='DSA Heldenbogen',
        native=True,
        window_size=(1280, 800),
        dark=True,
        host='127.0.0.1',
        reload=False,
    )