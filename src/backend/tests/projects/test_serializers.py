from api.v1.projects.serializers import ReadProjectSerializer


def test_owner_field(profile, project):
    valid_data = {
        "id": profile.user.id,
        "username": profile.user.username,
        "name": profile.name,
        "avatar": (profile.avatar.url if profile.avatar else None),
        "visible_status": profile.visible_status,
    }
    serializer = ReadProjectSerializer(instance=project)
    assert serializer.data["owner"] == valid_data
