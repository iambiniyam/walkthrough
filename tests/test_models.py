from walkthrough.models import Guide, Step


def test_guide_round_trip():
    guide = Guide(
        title="Export a report",
        summary="A two-step guide.",
        steps=[
            Step(
                number=1,
                image="step-1.png",
                title="Open Export",
                body="Select Export.",
                callout="Export",
                bbox=(10.0, 20.0, 100.0, 50.0),
                image_size=(800, 600),
                confidence=0.8,
            )
        ],
    )
    again = Guide.from_dict(guide.to_dict())
    assert again == guide
