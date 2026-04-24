import {
  Component,
  Output,
  EventEmitter,
  Input,
  signal,
  computed,
  forwardRef,
  inject,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ControlValueAccessor,
  FormControl,
  NG_VALUE_ACCESSOR,
  ReactiveFormsModule,
  ValidationErrors,
  AbstractControl,
} from '@angular/forms';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { IpInfoService } from '../../services/ip.service';
import { IpDetailsDialogComponent } from '../ip-details-dialog/ip-details-dialog.component';

export function ipValidator(control: AbstractControl): ValidationErrors | null {
  const value: string = control.value?.trim() || '';
  if (!value) return null;
  const ipv4 = /^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$/;
  const ipv6 = /^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|::|(([0-9a-fA-F]{1,4}:){1,7}:)|(([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4})|(([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2})|(([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3})|(([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4})|(([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5})|([0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6}))|(:((:[0-9a-fA-F]{1,4}){1,7}|:))|(fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,})|(::ffff(:0{1,4})?:((25[0-5]|(2[0-4]|1?\d)?\d)\.){3}(25[0-5]|(2[0-4]|1?\d)?\d))|(([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1?\d)?\d)\.){3}(25[0-5]|(2[0-4]|1?\d)?\d)))$/;
  if (ipv4.test(value) || ipv6.test(value)) return null;
  return { invalidIp: true };
}

@Component({
  selector: 'app-ip-input',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatDialogModule],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => IpInputComponent),
      multi: true,
    },
  ],
  templateUrl: './ip-input.component.html',
  styleUrls: ['./ip-input.component.css'],
})
export class IpInputComponent implements ControlValueAccessor {
  @Input() placeholder = 'e.g., 8.8.8.8 or 2001:db8::1';
  @Input() size: 'default' | 'large' = 'default';
  @Output() search = new EventEmitter<string>();

  private ipService = inject(IpInfoService);
  private dialog = inject(MatDialog);

  control = new FormControl('', [ipValidator]);

  isLoading = signal(false);
  isFocused = signal(false);
  isHovered = signal(false);

  isValid = computed(() => {
    return true;
    const v = this.control.value?.trim() || '';
    return v.length > 0 && !this.control.errors;
  });

  isInvalid = computed(() => {
    const v = this.control.value?.trim() || '';
    return v.length > 0 && !!this.control.errors;
  });

  ipVersion = computed(() => {
    const v = this.control.value?.trim() || '';
    if (!v) return null;
    const ipv4 = /^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$/;
    const ipv6 = /^([0-9a-fA-F]{1,4}:)/;
    if (ipv4.test(v)) return 'IPv4';
    if (ipv6.test(v)) return 'IPv6';
    return null;
  });

  private _onChange = (_: any) => {};
  private _onTouched = () => {};

  writeValue(val: string): void {
    this.control.setValue(val, { emitEvent: false });
  }
  registerOnChange(fn: any): void { this._onChange = fn; }
  registerOnTouched(fn: any): void { this._onTouched = fn; }

  onInput(): void {
    this._onChange(this.control.value);
  }

  onFocus(): void { this.isFocused.set(true); }
  onBlur(): void { this.isFocused.set(false); this._onTouched(); }
  onMouseEnter(): void { this.isHovered.set(true); }
  onMouseLeave(): void { this.isHovered.set(false); }

  onSearch(): void {
    const ip = this.control.value?.trim() || '';
    if (this.isValid() && !this.isLoading()) {
      this.isLoading.set(true);
      this.ipService.getIpInfo(ip).subscribe({
        next: (info) => {
          this.isLoading.set(false);
          this.search.emit(ip);
          
          this.dialog.open(IpDetailsDialogComponent, {
            data: info,
            width: '900px',
            maxWidth: '95vw',
            maxHeight: '85vh',
            panelClass: 'custom-dialog-container',
          });
        },
        error: (err) => {
          this.isLoading.set(false);
          console.error('Error fetching IP info:', err);
        }
      });
    }
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter') this.onSearch();
  }

  clear(): void {
    this.control.setValue('');
    this._onChange('');
  }
}
