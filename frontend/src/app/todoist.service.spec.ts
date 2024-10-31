import { TestBed } from '@angular/core/testing';

import { TodoistService } from './todoist.service';

describe('TodoistService', () => {
  let service: TodoistService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TodoistService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
