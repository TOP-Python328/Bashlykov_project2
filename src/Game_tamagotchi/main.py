import controller
import view


if __name__ == '__main__':
    
    app = controller.Application()
    root = view.RootWidget(app)
    app.link_view(root)
    
    app.run()

