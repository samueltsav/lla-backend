from rest_framework import serializers
from .models import Dashboard
from .models import LearningGoal


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = "__all__"


class LearningGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningGoal
        fields = "__all__"


class DashboardContentSerializer(serializers.Serializer):
    dashboard = DashboardSerializer()
    learning_goal = LearningGoalSerializer()
