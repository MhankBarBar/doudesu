from flet import (
    CircleAvatar,
    Column,
    Container,
    Row,
    Text,
    alignment,
    animation,
    colors,
    padding,
)


class LoadingAnimation(Container):
    def __init__(self, text: str = "Loading..."):
        super().__init__()

        # Create animated dots
        self.dots = [
            Container(
                content=CircleAvatar(
                    radius=5,
                    bgcolor=colors.BLUE,
                ),
                animate=animation.Animation(
                    1000,  # duration in milliseconds
                    "easeInOut",  # animation curve
                ),
            )
            for _ in range(3)
        ]

        # Store text control for easy access
        self.text = Text(
            text,
            color=colors.BLUE,
            size=16,
            weight="bold",
            text_align="center",
        )

        self.content = Column(
            [
                Container(
                    content=Row(
                        self.dots,
                        alignment="center",
                        spacing=8,
                    ),
                    padding=padding.only(bottom=10),
                ),
                Container(
                    content=self.text,
                    animate=animation.Animation(400, "easeOut"),
                ),
            ],
            horizontal_alignment=alignment.center,
            spacing=4,
        )

        self.bgcolor = colors.with_opacity(0.05, colors.ON_SURFACE)
        self.padding = padding.all(20)
        self.border_radius = 12
        self.visible = False
        self.expand = True

        # Set initial scale for dots
        for i, dot in enumerate(self.dots):
            dot.scale = 1.0
            # Offset the animation phase for each dot
            dot.animate.delay = i * 333  # Stagger the animations

    def did_mount(self):
        """Called when the control is added to page"""
        self.start_animation()

    def start_animation(self):
        """Start the pulsing animation"""
        for dot in self.dots:
            # Toggle scale to create continuous animation
            current_scale = dot.scale or 1.0
            dot.scale = 0.5 if current_scale == 1.0 else 1.0
            dot.update()

    @property
    def value(self) -> str:
        """Get the current text value"""
        return self.text.value

    @value.setter
    def value(self, val: str):
        """Set the text value"""
        self.text.value = val
