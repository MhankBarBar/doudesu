import flet as ft
from flet import (
    AnimationCurve,
    Column,
    Container,
    Icon,
    LinearGradient,
    Scale,
    Text,
    alignment,
    animation,
    colors,
    icons,
    padding,
    transform,
)


class LoadingAnimation(Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.visible = False
        self.bgcolor = colors.with_opacity(0.5, colors.BLACK)
        self.padding = padding.all(0)
        self.alignment = alignment.center

        self.spinner = Container(
            content=Icon(
                icons.AUTORENEW_ROUNDED,
                size=40,
                color=colors.PRIMARY,
            ),
            animate_rotation=animation.Animation(
                duration=1500,
                curve=AnimationCurve.LINEAR,
            ),
            rotate=transform.Rotate(0, alignment=alignment.center),
        )

        self.text = Container(
            content=Text(
                "Loading...",
                size=16,
                color=colors.ON_SURFACE_VARIANT,
                weight="w500",
            ),
            animate_scale=animation.Animation(
                duration=1000,
                curve=AnimationCurve.EASE_IN_OUT,
            ),
            scale=Scale(1),
        )

        self.shimmer = Container(
            width=200,
            height=4,
            border_radius=2,
            gradient=LinearGradient(
                begin=alignment.center_left,
                end=alignment.center_right,
                colors=[
                    colors.with_opacity(0.1, colors.PRIMARY),
                    colors.with_opacity(0.3, colors.PRIMARY),
                    colors.with_opacity(0.1, colors.PRIMARY),
                ],
            ),
            animate_position=animation.Animation(
                duration=1500,
                curve=AnimationCurve.EASE_IN_OUT,
            ),
        )

        inner_container = Container(
            content=Column(
                [
                    self.spinner,
                    self.text,
                    self.shimmer,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            bgcolor=colors.with_opacity(0.95, colors.BLACK54),
            padding=padding.all(40),
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=colors.with_opacity(0.1, colors.SHADOW),
                offset=ft.Offset(0, 2),
            ),
        )

        self.content = ft.Stack(
            [
                # Container(
                #     expand=True,
                #     bgcolor=colors.with_opacity(0.5, colors.BLACK),
                # ),
                Container(
                    content=inner_container,
                    alignment=alignment.center,
                    expand=True,
                ),
            ],
        )

    def did_mount(self):
        """Start animations when component mounts"""
        self.spinner.rotate.angle = 360
        self.spinner.update()

        self.text.scale = Scale(0.95)
        self.text.update()

        self.shimmer.left = -200
        self.shimmer.update()

    def will_unmount(self):
        """Stop animations when component unmounts"""
        self.spinner.rotate.angle = 0
        self.text.scale = Scale(1)
        self.shimmer.left = 0

    @property
    def value(self) -> str:
        """Get the current text value"""
        return self.text.content.value

    @value.setter
    def value(self, val: str):
        """Set the text value"""
        self.text.content.value = val
