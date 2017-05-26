/***************************************************************************

Copyright (c) 2016, EPAM SYSTEMS INC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

****************************************************************************/

import { Injectable } from '@angular/core';
import { Response } from '@angular/http';
import { Observable } from 'rxjs/Observable';

import { ApplicationServiceFacade } from './';

@Injectable()
export class LibrariesInstallationService {

    constructor(private applicationServiceFacade: ApplicationServiceFacade) { }

    public getGroupsList(data): Observable<Response> {
        return this.applicationServiceFacade
        .buildGetGroupsList(data)
        .map((response: Response) => response.json());
    }

    public getAvailableLibrariesList(data): Observable<Response> {
        return this.applicationServiceFacade
        .buildGetAvailableLibrariesList(data)
        .map((response: Response) => response.json());
    }

    public installLibraries(data): Observable<Response> {
        return this.applicationServiceFacade
        .buildInstallLibraries(data)
        .map((response: Response) => response);
    }
}
