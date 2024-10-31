import { TestBed } from '@angular/core/testing';

import { TodoistService } from './todoist.service';
import { provideHttpClient } from '@angular/common/http';

describe('TodoistService', () => {
  let service: TodoistService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient()]
    });
    service = TestBed.inject(TodoistService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
