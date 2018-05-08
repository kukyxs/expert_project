from rest_framework import serializers

from expert_skill.models import Category, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skill_name', 'skill_description']


class CategorySerializer(serializers.ModelSerializer):
    skill = SkillSerializer(many=True)

    class Meta:
        model = Category
        fields = '__all__'
