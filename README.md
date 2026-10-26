# Module 1 Group Assignment

CSCI 5117, Fall 2026, [assignment description](https://canvas.umn.edu/courses/579310/pages/project-1)

## App Info:

* Team Name: Yarakani
* App Name: Lost and Found
* App Link: [https://lost-and-found-88jm.onrender.com/](https://lost-and-found-88jm.onrender.com/)

### Students

* Nipun Bhatnagar, bhatn058@umn.edu
* Yassir Abdalla, abdal167@umn.edu
* Ray Amberg, amber079@umn.edu
* Kane Stirling stirl027@umn.edu
* Blake Gabriel gabri354@umn.edu


## Key Features

**Describe the most challenging features you implemented
(one sentence per bullet, maximum 4 bullets):**

* Login restriction that prevents non-UMN from registering with the site across email and Sign In With Google.
* Database pooling, mostly as a result of debugging the strange errors from gunicorn.

## Testing Notes

**Is there anything special we need to know in order to effectively test your app? (optional):**

* Must utilize a verified umn.edu email address to register.


## Screenshots of Site

**[Add a screenshot of each key page (around 4)](https://stackoverflow.com/questions/10189356/how-to-add-screenshot-to-readmes-in-github-repository)
along with a very brief caption:**

![](https://media.giphy.com/media/o0vwzuFwCGAFO/giphy.gif)


## Mock-up 

### 1. Home page

![Home feed mockup](docs/mockups/1-home-feed.png)

*Main page most users will experience. Displays recently found items with filters for specific building and item types*

### 2. Item page

![Item page mockup](docs/mockups/2-item-page.png)

*Detail view for a single found item: photo, description, where to pick it up with a map image, and a comment section Edit and delet buttons only appear when the user is the original creator of the post*

### 3. Create post

![Post found item mockup](docs/mockups/3-post-found-item.png)

*Form for creating a post including a generated textboc at the bottom prompting the user to drop off the item*

### 4. Log in

![Log in mockup](docs/mockups/4-log-in-basic.png)

*Sign-in page restricted to umn email*

### 5. My posts

![My posts mockup](docs/mockups/5-my-posts.png)

*A user's own posted items in a table, with comment counts and edit/delete actions for each one.*


## External Dependencies

**Document integrations with 3rd Party code or services here.
Please do not document required libraries. or libraries that are mentioned in the product requirements**

* Leaflet: interactive maps on he location and item pages
* OpenStreetMap: map tiles for Leaflet, plus the building addresses and coordinates

**If there's anything else you would like to disclose about how your project
relied on external code, expertise, or anything else, please disclose that
here:**

...
