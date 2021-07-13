from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    reverse,
    get_object_or_404,
)
from cuser.forms import RegisterForm
from django.forms import inlineformset_factory
from .forms import (
    UserForm,
    RecipeForm,
    RIForm,
    CommentForm,
)
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from .models import ( 
    UserInfo,
    Category, 
    Recipe,
    Comment,
    Report,
    Recipe_Ingredient,
)
# Create your views here.

def index(request):
    """ The function to render homepage of the app """
    return render(request, 'app_recipe/cookit.html')

class UserLogin(LoginView):
    """ The login view for the user """
    template_name = 'app_recipe/login.html'
    # success_url = 'app_recipe:index_page'
    LOGIN_REDIRECT_URL = 'app_recipe:index_page'

def RegisterUser(request):
    """ User registration """
    if request.method == 'POST':
        reg_form = RegisterForm(request.POST or None)
        user_form = UserForm(request.POST or None)
        if user_form.is_valid() and reg_form.is_valid():
            print(user_form.cleaned_data, reg_form.cleaned_data)
            reg_user    = reg_form.save()
            user_data   = user_form.save(commit= False)
            user_data.user = reg_user
            user_data.save()
            return redirect(reverse('app_recipe:login_view'))
    else:
        reg_form = RegisterForm()
        user_form = UserForm()
    return render(request, 'app_recipe/register.html', {
        'form1' : reg_form,
        'form2' : user_form,
    })

@login_required(login_url = 'app_recipe:login_view')
def AddRecipe(request):
    """ Function to add recipes """
    user    = request.user
    RForm   = RecipeForm(initial = {'created_by' : user})
    RIFForm = inlineformset_factory(Recipe, Recipe_Ingredient, fields= ('ingredient', 'amount'))
    formset = RIFForm(instance= None)
    if request.method == 'POST':
        RForm   = RecipeForm(request.POST or None)
        if RForm.is_valid():
            recipedata      = RForm.save(commit=False)
            recipedata.created_by = request.user
            recipedata.save()
            # saveFormSet     = formset.save(commit= False)
            formset = RIFForm(request.POST or None, instance= recipedata)
            if formset.is_valid():
                formset.save()
            return redirect(reverse('app_recipe:index_page'))

    return render(request,
     'app_recipe/recipe_add.html',
     {
        'RForm' : RForm,
        'formset' : formset,  
     }
    )

def viewRecipe(request, id):
    """ The function to view the info about a certain recipe """
    recipe      = get_object_or_404(Recipe,id = id )
    ingredients = {}
    if recipe:
        if request.method == "POST":
            form = CommentForm(request.POST or None)
            if form.is_valid():
                user = request.user
                form.save(commit = False)
                form.created_by = user
                # recipe_id = Recipe.objects.get(id = id)
                form.recipe = recipe
                form.save()
        ingredients   = Recipe_Ingredient.objects.filter(recipe = recipe)
    # print(recipe[0].recipe_name, "and" , ingredients)
        return render(request, 'app_recipe/recipe_details.html',
            {
                'recipeInfo' : recipe,
                'ingredients' : ingredients,
                'message'     : None,
                'form'        : CommentForm()
            }
        )
    return render(request, 'app_recipe/recipe_details.html',
            {
                'recipeInfo' : None,
                'ingredients' : ingredients,
                'form'        : CommentForm(), 
                'message'     : "Recipe doesn't exist",
            })

@login_required(login_url = 'app_recipe:login_view')
def updateRecipe(request,id):
    """ Function to add recipes """
    user    = request.user
    instance= Recipe.objects.get(id = id)
    if user != instance.created_by:
        return redirect(reverse('app_recipe:index_page'))
    RForm   = RecipeForm(initial = {'created_by' : user}, instance= instance )
    RIFForm = inlineformset_factory(Recipe, Recipe_Ingredient, fields= ('ingredient', 'amount'))
    formset = RIFForm(instance= instance)
    if request.method == 'POST':
        RForm   = RecipeForm(request.POST or None, instance= instance)
        if RForm.is_valid():
            recipedata      = RForm.save(commit=False)
            recipedata.created_by = request.user
            recipedata.save()
            # saveFormSet     = formset.save(commit= False)
            formset = RIFForm(request.POST or None, instance= recipedata)
            if formset.is_valid():
                formset.save()
            return redirect(reverse('app_recipe:index_page'))

    return render(request,
     'app_recipe/recipe_add.html',
     {
        'RForm' : RForm,
        'formset' : formset,  
     }
    )