# Basketify_SBX

## Description
Basketify was completed as our final-year engineering capstone project for ECE 493.

The project implements a full-stack web app which allows users to view NBA statsistics and
see ML predictions for upcoming games and the overall NBA champion.

To run the project locally (run the web server so that it can be accessed on the local network), see
test_server/RUNNING_INSTRUCTIONS.txt.

Backend (Django) test cases can be executed by the following:
(Follow all instructions at RUNNING_INSTRUCTIONS.txt first)
$ cd backend
$ python3 manage.py test

Frontend/Acceptance tests (React/JS) can be executed by the following:
$ cd frontend
$ npm install --save-dev @testing-library/react @babel/preset-env @babel/preset-react babel-jest
$ npm test
(to see coverage statistics run it as: npm test -- --coverage)

## Developers
- Aron Gu (arongu321)
- Zachary Schmidt (ZacharySchmidt0)
- Muhammed Rayyan Rashid (rayyanrashid02)
