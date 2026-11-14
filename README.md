## Testing

Run the automated tests using:

```bash
python manage.py test
```

The project includes tests for unit creation, form validation, healing, fight simulation, fight history, and statistics.

## Demonstration

1. Start the application using `python manage.py runserver`.
2. Visit `/unit` to create fighters for the Blue and Red teams.
3. Visit `/unit/all` to view the fighters.
4. Select two fighters from opposing teams and simulate a battle.
5. View the fight history, winner, and team statistics.
6. Heal damaged fighters using the Heal button.

## Technologies

- Python
- Django
- SQLite
- HTML and CSS

## Development Notes

The application uses Django's development server and SQLite database. Production deployment requires appropriate security and configuration settings.
