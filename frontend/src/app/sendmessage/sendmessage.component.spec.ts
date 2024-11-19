import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SendmessageComponent } from './sendmessage.component';

describe('SendmessageComponent', () => {
    let component: SendmessageComponent;
    let fixture: ComponentFixture<SendmessageComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [SendmessageComponent]
        })
            .compileComponents();

        fixture = TestBed.createComponent(SendmessageComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
