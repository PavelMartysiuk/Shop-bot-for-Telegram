# Shop bot for Telegram


# Database
	Bot has the postgresql database. You should use two talbles for load products.
	Fist table is category. second tables is dish.
	***
	How load products to batabse?
	First of the all you should load the categories to category tables.
	After filling in the category table, you need to fill in the dish table
	***
	*Category table structure*
		id
		:	id field stores id of category(autoadd)
		category_name
		:	category_name stores name of category(type is string)
	***
	*Dish table structure*
		id
		:	id field stores id of dish(autoadd)
		dish_name
		:	dish_name stores name of dish(type is string)
		image
		:	image stores photo of dish(type is binary)
		catgory
		:	category stores id of dish category(type is ForeigKey of category_id field in catagory table)
		cost
		:	cost stores cost of dish(type is string)
		content
		:	content stores discrition of dish(type is string)
		page
		:	User shooses the category and after bot sends list of dish in current category with paginator.
			Optimal quantity of dish on one page of pagenator is five.The Page field is used for store the number of paginator page for this dish.
			Field type is integer.
	
			
 
	



