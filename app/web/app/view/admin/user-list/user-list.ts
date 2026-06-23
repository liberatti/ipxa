import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { UserService } from '../../../services/user.service';
import { User } from '../../../models/user';
import { UserFormComponent } from '../user-form/user-form';
import { DefaultPageMeta, PageMeta } from 'app/models/shared';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule, MatTableModule, MatButtonModule, MatIconModule, MatCardModule, MatDialogModule, MatPaginatorModule],
  templateUrl: './user-list.html',
  styleUrls: ['./user-list.css']
})
export class UserListComponent implements OnInit {
  userDC: string[] = ['name', 'email', 'role', 'actions'];
  userDS: MatTableDataSource<User>;
  userPA: PageMeta;

  constructor(
    private userService: UserService,
    private dialog: MatDialog
  ) {
    this.userDS = new MatTableDataSource<User>();
    this.userPA = new DefaultPageMeta();
  }

  ngOnInit() {
    this.updateGridTable();
  }

  updateGridTable() {
    this.userService.get(this.userPA).subscribe({
      next: (res: any) => {
        if (res && res.metadata) {
          this.userPA.total_elements = res.metadata.total_elements;
          this.userDS.data = res.data;
        } else if (res && Array.isArray(res.data)) {
          this.userDS.data = res.data;
          this.userPA.total_elements = res.data.length;
        } else if (res && Array.isArray(res)) {
          this.userDS.data = res;
          this.userPA.total_elements = res.length;
        } else {
          this.userDS.data = [];
          this.userPA.total_elements = 0;
        }
      },
      error: () => {
        this.userDS.data = [];
        this.userPA.total_elements = 0;
      }
    });
  }

  openForm(user?: User) {
    const dialogRef = this.dialog.open(UserFormComponent, {
      data: user || null,
      width: '600px',
      panelClass: 'custom-dialog-container'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        if (user?._id) {
          this.userService.update(user._id, result).subscribe(() => this.updateGridTable());
        } else {
          this.userService.save(result).subscribe(() => this.updateGridTable());
        }
      }
    });
  }

  onRemove(id: number) {
    if (confirm('Are you sure you want to delete this user?')) {
      this.userService.removeById(id).subscribe(() => this.updateGridTable());
    }
  }

  nextPage(event: PageEvent) {
    this.userPA.page = event.pageIndex + 1;
    this.userPA.per_page = event.pageSize;
    this.updateGridTable();
  }
}
