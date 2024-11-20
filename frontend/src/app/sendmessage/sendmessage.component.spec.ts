import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { SendmessageComponent } from './sendmessage.component';
import { getBackendURL } from '../../config';

describe('SendmessageComponent', () => {
    let component: SendmessageComponent;
    let fixture: ComponentFixture<SendmessageComponent>;
    let httpMock: HttpTestingController;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [SendmessageComponent, HttpClientTestingModule, ReactiveFormsModule]
        })
            .compileComponents();

        fixture = TestBed.createComponent(SendmessageComponent);
        component = fixture.componentInstance;
        httpMock = TestBed.inject(HttpTestingController);
        fixture.detectChanges();
    });

    it('Creating the SendMessage component', () => {
        expect(component).toBeTruthy();
    });

    it('Should disable send message button while sending', fakeAsync(() => {
        expect(component.isSendingMessage).toBeFalse();
        component.recipientsIds = [1];
        component.messageForm.controls['subject'].setValue('Test Subject');
        component.messageForm.controls['body'].setValue('Test Body');

        component.sendMessage();
        expect(component.isSendingMessage).toBeTrue();

        const req = httpMock.expectOne(getBackendURL() + '/api/v1/user/send_message');
        expect(req.request.method).toBe('POST');
        req.flush({});

        tick();
        expect(component.isSendingMessage).toBeFalse();
    }));

    it('Should disable reply button while sending reply', fakeAsync(() => {
        const conversationId = 1;
        component.replyTexts[conversationId] = 'Test Reply';

        component.sendReply(conversationId);
        expect(component.isSendingReply[conversationId]).toBeTrue();

        const req = httpMock.expectOne(getBackendURL() + '/api/v1/user/reply_message');
        expect(req.request.method).toBe('POST');
        req.flush({});

        tick();
        expect(component.isSendingReply[conversationId]).toBeFalse();
    }));

    it('Call switchTab method', () => {
        spyOn(component, 'switchTab');
        const tabButton = fixture.nativeElement.querySelector('.tab-button');
        tabButton.click();
        expect(component.switchTab).toHaveBeenCalled();
    });

    it('Call toggleRecipientSelection method', () => {
        spyOn(component, 'toggleRecipientSelection');
        const selectElement = fixture.nativeElement.querySelector('#recipients');
        const event = new Event('change');
        selectElement.dispatchEvent(event);
        expect(component.toggleRecipientSelection).toHaveBeenCalled();
    });

    it('Call removeRecipient method', () => {
        spyOn(component, 'removeRecipient');
        component.selectedRecipients = [{ id: 1, name: 'Recipient 1' }];
        fixture.detectChanges();
        const recipientButton = fixture.nativeElement.querySelector('.selected-recipient');
        recipientButton.click();
        expect(component.removeRecipient).toHaveBeenCalledWith(1);
    });

    afterEach(() => {
        httpMock.verify();
    });
});
